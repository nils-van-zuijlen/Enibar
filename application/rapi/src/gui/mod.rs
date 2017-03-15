use cpython::{PyModule, Python, PyBool, PyResult};

pub mod password_prompt;
pub mod utils;
use gtk;
use self::password_prompt::*;


pub fn check_password(py: Python, manage_notes: bool, manage_users: bool, manage_products: bool) -> PyResult<(PyBool, PyBool)> {
    let prompt = PasswordPrompt::new(manage_notes, manage_users, manage_products);
    gtk::main();
    let prompt = prompt.borrow();
    let result = prompt.is_authorized;
    let error = prompt.is_error;
    Ok((PyBool::get(py, result), PyBool::get(py, error)))
}

// This should be called only ONCE !
pub fn as_module(py: Python) -> PyModule {
    if gtk::init().is_err() {
        panic!("Failed to initialize GTK.");
    }

    let module = PyModule::new(py, "gui").unwrap();
    let _ = module.add(py, "check_password", py_fn!(py, check_password(manage_notes: bool, manage_users: bool, manage_products: bool)));
    module
}
