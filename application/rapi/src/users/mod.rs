pub mod models;
mod py;

use self::models::*;
use bcrypt::{DEFAULT_COST, hash, verify};
use cpython::{PyModule, Python};
use diesel::prelude::*;
use diesel;
use errors::*;
use errors::ErrorKind::*;
use ::schema::admins;
use self::py::*;

impl User {
    /// Adds an user with default rights.
    pub fn add(conn: &PgConnection, username: &str, password: &str) -> Result<User> {
        if username == "" || password == "" {
            return Err(Error::from(UserCreationError("The login and the password mustn't be empty".into())))
        }

        let hash = if cfg!(test) {
            hash(&password, 4)?
        } else {
            hash(&password, DEFAULT_COST)?
        };

        let user = NewUser { login: &username, password: &hash };

        diesel::insert(&user)
            .into(::schema::admins::table)
            .get_result::<User>(conn)
            .map_err(|e| e.into())
    }

    /// Checks that the hash of password of the provided user matches the provided password
    pub fn is_authorized(&self, password: &str) -> Result<bool> {
        verify(password, &self.password).map_err(|e| e.into())
    }

    /// Change the password of the user
    pub fn change_password(self, conn: &PgConnection, new_password: &str) -> Result<User> {
        let hash = if cfg!(test) {
            hash(new_password, 4)?
        } else {
            hash(new_password, DEFAULT_COST)?
        };

        diesel::update(
            admins::table
            .find(self.login.clone()))
            .set(admins::password.eq(&hash)
        ).get_result::<User>(conn)
            .map_err(|e| e.into())
    }

    pub fn get(conn: &PgConnection, username: &str) -> Result<User> {
        admins::table.filter(admins::login.eq(username)).first::<User>(conn).map_err(|e| e.into())
    }
}


pub fn as_module(py: Python) -> PyModule {
    let module = PyModule::new(py, "users").unwrap();
    let _ = module.add(py, "add", py_fn!(py, py_add(username: String, password: String)));
    let _ = module.add(py, "is_authorized", py_fn!(py, py_is_authorized(username: String, hash: String)));
    let _ = module.add(py, "change_password", py_fn!(py, py_change_password(username: String, new_password: String)));
    module
}
