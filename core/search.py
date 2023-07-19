import sys
import os
import traceback
import win32con as wcon
import win32api as wapi
import win32gui as wgui
import win32process as wproc


# Callback
def enum_windows_proc(wnd, param):
    pid = param.get("pid", None)
    data = param.get("data", None)
    if pid is None or wproc.GetWindowThreadProcessId(wnd)[1] == pid:
        text = wgui.GetWindowText(wnd)
        if text:
            style = wapi.GetWindowLong(wnd, wcon.GWL_STYLE)
            if style & wcon.WS_VISIBLE:
                if data is not None:
                    data.append((wnd, text))
                # else:
                # print("%08X - %s" % (wnd, text))


def enum_process_windows(pid=None):
    data = []
    param = {
        "pid": pid,
        "data": data,
    }
    wgui.EnumWindows(enum_windows_proc, param)
    return data


def _filter_processes(processes, search_name=None):
    if search_name is None:
        return processes
    filtered = []
    for pid, _ in processes:
        try:
            proc = wapi.OpenProcess(wcon.PROCESS_ALL_ACCESS, 0, pid)
        except:
            # print("Process {0:d} couldn't be opened: {1:}".format(pid, traceback.format_exc()))
            continue
        try:
            file_name = wproc.GetModuleFileNameEx(proc, None)
        except:
            # print("Error getting process name: {0:}".format(traceback.format_exc()))
            wapi.CloseHandle(proc)
            continue
        base_name = file_name.split(os.path.sep)[-1]
        if base_name.lower() == search_name.lower():
            filtered.append((pid, file_name))
        wapi.CloseHandle(proc)
    return tuple(filtered)


def enum_processes(process_name=None):
    procs = [(pid, None) for pid in wproc.EnumProcesses()]
    return _filter_processes(procs, search_name=process_name)


def search(*args):
    proc_name = args[0] if args else None
    procs = enum_processes(process_name=proc_name)
    for pid, name in procs:
        data = enum_process_windows(pid)
        if data:
            proc_text = "PId {0:d}{1:s}windows:".format(pid, " (File: [{0:s}]) ".format(name) if name else " ")
            for handle, text in data:
                return text
