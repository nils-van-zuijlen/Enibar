#![allow(unknown_lints)]

extern crate bcrypt;
extern crate bigdecimal;
extern crate byteorder;
extern crate chrono;
#[macro_use]
extern crate cpython;
#[macro_use]
extern crate diesel;
#[macro_use]
extern crate error_chain;
#[macro_use]
extern crate lazy_static;
extern crate num_traits;
#[macro_use]
extern crate rapi_codegen;
extern crate redis;
extern crate validator;
#[macro_use]
extern crate validator_derive;
extern crate x11;

#[macro_use]
mod py_helpers;
pub mod categories;
mod errors;
pub mod utils;
pub mod users;
pub mod schema;
pub mod model;
mod validators;
pub mod note_categories;
pub mod panels;
pub mod products;
mod diesel_helpers;
pub mod notes;

pub use model::Model;

#[cfg(test)]
mod tests;

use cpython::Python;
use diesel::PgConnection;
use diesel::r2d2::ConnectionManager;
use std::env;
use redis::Commands;

pub(crate) use diesel_helpers::*;

lazy_static! {
    pub static ref DB_POOL: diesel::r2d2::Pool<ConnectionManager<PgConnection>> = {
        let manager = ConnectionManager::<PgConnection>::new(
            match env::var("DATABASE_URL") {
                Ok(val) => val,
                Err(_) => {
                    let gil = Python::acquire_gil();
                    let py = gil.python();
                    let settings = py.import("settings").expect("Can't import the settings module");
                    let redis_host = settings.get(py, "REDIS_HOST").expect("No REDIS_HOST in settings");
                    let url = format!("redis://{}/", redis_host);
                    let client = redis::Client::open(url.as_str()).expect("Can't connect to redis");
                    let con = client.get_connection().expect("Can't connect to redis²");
                    let host: String = con.get("DB_HOST").expect("Can't find the database url in redis");
                    let user: String = con.get("USERNAME").expect("Can't find the database username in redis");
                    let password: String = con.get("PASSWORD").expect("Can't find the database password in redis");
                    let db_name: String = con.get("DBNAME").expect("Can't find the database url in redis");
                    format!("postgres://{}:{}@{}/{}", user, password, host, db_name)
                }
            }
        );

        diesel::r2d2::Pool::builder().build(manager).expect("Failed to connect to psql")
    };
}

