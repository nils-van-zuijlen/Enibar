use cpython::{PyBool, PyModule, PyResult, Python};
use x11::xlib;
use std::ptr;

pub fn check_x11(py: Python) -> PyResult<PyBool> {
    unsafe {
        let display = xlib::XOpenDisplay(ptr::null());
        Ok(PyBool::get(py, display.is_null()))
    }
}

pub fn as_module(py: Python) -> PyModule {
    let module = PyModule::new(py, "utils").unwrap();
    let _ = module.add(py, "check_x11", py_fn!(py, check_x11()));
    module
}
