#[macro_use]
extern crate cpython;
extern crate rapi;
use rapi::*;

py_module_initializer!(rapi, initrapi, PyInit_rapi, |py, m| {
    m.add(py, "utils", utils::as_module(py))?;
    m.add(py, "users", users::as_module(py))?;
    m.add(py, "categories", categories::as_module(py))?;
    m.add(py, "note_categories", note_categories::as_module(py))?;
    m.add(py, "panels", panels::as_module(py))?;
    m.add(py, "products", products::as_module(py))?;
    m.add(py, "notes", notes::as_module(py))?;
    Ok(())
});
