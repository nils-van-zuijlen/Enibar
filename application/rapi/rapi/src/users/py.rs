use users::models::*;
use cpython::{PyBool, PyDict, PyResult, Python};

pub fn py_add(py: Python, username: &str, password: &str) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    match User::add(&*conn, username, password) {
        Err(_) => Ok(PyBool::get(py, false)),
        Ok(_) => Ok(PyBool::get(py, true)),
    }
}

pub fn py_is_authorized(py: Python, username: &str, hash: &str) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();
    let user = User::get(&*conn, username);

    if let Ok(user) = user {
        let is_authorized = user.is_authorized(hash);
        if let Ok(is_authorized) = is_authorized {
            return Ok(PyBool::get(py, is_authorized));
        }
    }
    Ok(PyBool::get(py, false))
}

pub fn py_change_password(py: Python, username: &str, new_password: &str) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();
    let user = User::get(&*conn, username);

    let is_ok = if let Ok(user) = user {
        user.change_password(&*conn, new_password).is_ok()
    } else {
        false
    };

    Ok(PyBool::get(py, is_ok))
}

pub fn py_remove(py: Python, username: &str) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();
    let user = User::get(&*conn, username);

    if let Ok(user) = user {
        match user.remove(&*conn) {
            Err(_) => return Ok(PyBool::get(py, false)),
            Ok(_) => return Ok(PyBool::get(py, true)),
        }
    }

    Ok(PyBool::get(py, false))
}

pub fn py_get_rights(py: Python, username: &str) -> PyResult<PyDict> {
    let conn = ::DB_POOL.get().unwrap();
    let user = User::get(&*conn, username);

    if let Ok(user) = user {
        return dict!(py,
                     {"manage_notes" => user.manage_notes,
                     "manage_users" => user.manage_users,
                     "manage_products" => user.manage_products}
                    );
    }

    dict!(py,
          {"manage_notes" => false,
          "manage_users" => false,
          "manage_products" => false}
    )
}
