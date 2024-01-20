package main

import (
	"crypto/aes"
	"crypto/md5"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"math/rand"
	"net/http"
	netUrl "net/url"
	"strconv"
	"strings"
	"time"
)

func main() {
	userid := flag.Int("userid", 0, "User ID")
	flag.Parse()
	if *userid == 0 {
		fmt.Println("Please input user id")
		return
	}
	data := RequestData{}
	result, _ := GetUserStatus(data, *userid)
	jsonData, err := json.MarshalIndent(result, "", "  ")
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(string(jsonData))
}

var DEBUG bool

const eapiKey = "e82ckenh8dichen8"

type RequestData struct {
	Cookies []*http.Cookie
	Headers Headers
	Body    string
}
type Headers []struct {
	Name  string
	Value string
}
type UserStatusDetailData struct {
	RawJson string `json:"-"`
	Code    int    `json:"code"`
	Data    struct {
		Id       int         `json:"id"`
		UserId   int         `json:"userId"`
		Avatar   string      `json:"avatar"`
		UserName string      `json:"userName"`
		Song     interface{} `json:"song"`
		Content  struct {
			Type      string      `json:"type"`
			IconUrl   string      `json:"iconUrl"`
			Content   string      `json:"content"`
			ActionUrl interface{} `json:"actionUrl"`
		} `json:"content"`
		ExtInfo interface{} `json:"extInfo"`
	} `json:"data"`
	Message string `json:"message"`
}
type EapiOption struct {
	Json string
	Path string
	Url  string
}
type userStatusDetailReqJson struct {
	VisitorId int `json:"visitorId"`
}

const UserStatusDetailAPI = "/api/social/user/status/detail"

func GetUserStatus(data RequestData, userID int) (result UserStatusDetailData, err error) {
	var options EapiOption
	options.Path = UserStatusDetailAPI
	options.Url = "https://music.163.com/eapi/social/user/status/detail"
	options.Json = CreateUserStatusDetailReqJson(userID)
	resBody, _, err := ApiRequest(options, data)
	if err != nil {
		return result, err
	}
	err = json.Unmarshal([]byte(resBody), &result)
	result.RawJson = resBody
	return result, err
}

func CreateUserStatusDetailReqJson(visitorId int) string {
	reqBodyJson, _ := json.Marshal(userStatusDetailReqJson{
		VisitorId: visitorId,
	})
	return string(reqBodyJson)
}

func ApiRequest(eapiOption EapiOption, options RequestData) (result string, header http.Header, err error) {
	data := SpliceStr(eapiOption.Path, eapiOption.Json)
	answer, header, err := CreateNewRequest(Format2Params(data), eapiOption.Url, options)
	if err == nil {
		if DEBUG {
			log.Printf("[RespBodyJson]: %s", answer)
			log.Printf("[RespHeader]: %s", header)
		}
		return answer, header, nil
	}
	return "", header, err
}
func SpliceStr(path string, data string) (result string) {
	nobodyKnowThis := "36cd479b6b5"
	text := fmt.Sprintf("nobody%suse%smd5forencrypt", path, data)
	MD5 := md5.Sum([]byte(text))
	md5str := fmt.Sprintf("%x", MD5)
	result = fmt.Sprintf("%s-%s-%s-%s-%s", path, nobodyKnowThis, data, nobodyKnowThis, md5str)
	return result
}

func CreateNewRequest(data string, url string, options RequestData) (answer string, resHeader http.Header, err error) {
	client := &http.Client{}
	reqBody := strings.NewReader(data)
	req, err := http.NewRequest("POST", url, reqBody)
	if err != nil {
		return "", resHeader, err
	}

	cookie := map[string]interface{}{}
	for _, v := range options.Cookies {
		cookie[v.Name] = v.Value
	}

	for _, v := range options.Headers {
		req.Header.Set(v.Name, v.Value)
	}

	cookie["appver"] = "8.9.70"
	cookie["buildver"] = strconv.FormatInt(time.Now().Unix(), 10)[0:10]
	cookie["resolution"] = "1920x1080"
	cookie["os"] = "android"

	_, ok := cookie["MUSIC_U"]
	if !ok {
		_, ok := cookie["MUSIC_A"]
		if !ok {
			cookie["MUSIC_A"] = "4ee5f776c9ed1e4d5f031b09e084c6cb333e43ee4a841afeebbef9bbf4b7e4152b51ff20ecb9e8ee9e89ab23044cf50d1609e4781e805e73a138419e5583bc7fd1e5933c52368d9127ba9ce4e2f233bf5a77ba40ea6045ae1fc612ead95d7b0e0edf70a74334194e1a190979f5fc12e9968c3666a981495b33a649814e309366"
		}
	}

	var cookies string
	for key, val := range cookie {
		cookies += encodeURIComponent(key) + "=" + encodeURIComponent(fmt.Sprintf("%v", val)) + "; "
	}
	req.Header.Set("Cookie", strings.TrimRight(cookies, "; "))

	if len(req.Header["Content-Type"]) == 0 {
		req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	}

	req.Header.Set("User-Agent", ChooseUserAgent())

	if DEBUG {
		log.Printf("[Request]: %+v", req)
		if len([]byte(data)) < 51200 {
			log.Printf("[ReqBody]: %+v", data)
		}
	}

	resp, err := client.Do(req)
	if err != nil {
		return "", resHeader, err
	}

	defer func(Body io.ReadCloser) {
		err := Body.Close()
		if err != nil {
			log.Println(err)
		}
	}(resp.Body)

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", resHeader, err
	}

	return string(body), resp.Header, nil
}
func Format2Params(str string) (data string) {
	data = fmt.Sprintf("params=%X", EapiEncrypt(str))
	return data
}
func EapiEncrypt(data string) (encrypted []byte) {
	return encryptECB(data, eapiKey)
}
func encryptECB(data, keyStr string) (encrypted []byte) {
	origData := []byte(data)
	key := []byte(keyStr)
	cipher, _ := aes.NewCipher(generateKey(key))
	length := (len(origData) + aes.BlockSize) / aes.BlockSize
	plain := make([]byte, length*aes.BlockSize)
	copy(plain, origData)
	pad := byte(len(plain) - len(origData))
	for i := len(origData); i < len(plain); i++ {
		plain[i] = pad
	}
	encrypted = make([]byte, len(plain))
	// 分组分块加密
	for bs, be := 0, cipher.BlockSize(); bs <= len(origData); bs, be = bs+cipher.BlockSize(), be+cipher.BlockSize() {
		cipher.Encrypt(encrypted[bs:be], plain[bs:be])
	}

	return encrypted
}
func encodeURIComponent(str string) string {
	r := netUrl.QueryEscape(str)
	r = strings.Replace(r, "+", "%20", -1)
	return r
}

func generateKey(key []byte) (genKey []byte) {
	genKey = make([]byte, 16)
	copy(genKey, key)
	for i := 16; i < len(key); {
		for j := 0; j < 16 && i < len(key); j, i = j+1, i+1 {
			genKey[j] ^= key[i]
		}
	}
	return genKey
}

// ChooseUserAgent 随机 UserAgent
func ChooseUserAgent() string {
	userAgentList := []string{
		"Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
		"Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
		"Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36",
		"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36",
		"Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36",
		"Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Mobile/14F89;GameHelper",
		"Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 Mobile/14A300 Safari/602.1",
		"NeteaseMusic/6.5.0.1575377963(164);Dalvik/2.1.0 (Linux; U; Android 9; MIX 2 MIUI/V12.0.1.0.PDECNXM)",
	}
	rand.Seed(time.Now().UnixNano())
	var index int = rand.Intn(len(userAgentList))
	return userAgentList[index]
}
