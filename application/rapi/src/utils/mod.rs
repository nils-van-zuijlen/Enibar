use cpython::{PyModule, Python, PyBool, PyResult};
use x11::xlib;
use std::ptr;

pub fn check_x11(py: Python) -> PyResult<PyBool> {
    unsafe {
        let display = xlib::XOpenDisplay(ptr::null());
        if display.is_null() {
            Ok(py.False())
        }
        else{
            Ok(py.True())
        }
    }
}

pub fn as_module(py: Python) -> PyModule {
    let module = PyModule::new(py, "utils").unwrap();
    let _ = module.add(py, "check_x11", py_fn!(py, check_x11()));
    module
}
