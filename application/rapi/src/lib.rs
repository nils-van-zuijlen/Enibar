#[macro_use] extern crate cpython;
extern crate x11;

use cpython::{PyObject, PyResult, Python, PyTuple, PyDict};
mod utils;

py_module_initializer!(rapi, initrapi, PyInit_rapi, |py, m| {
    m.add(py, "utils", utils::as_module(py))?;
    Ok(())
});
