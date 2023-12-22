import ctypes

def get_active_window_process_and_title():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    window_title = ctypes.create_unicode_buffer(255)
    ctypes.windll.user32.GetWindowTextW(hwnd, window_title, ctypes.sizeof(window_title))
    process_id = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
    process_handle = ctypes.windll.kernel32.OpenProcess(0x0400 | 0x0010, False, process_id.value)
    process_name = ctypes.create_unicode_buffer(255)
    ctypes.windll.psapi.GetModuleBaseNameW(process_handle, None, process_name, ctypes.sizeof(process_name))
    return process_name.value, window_title.value