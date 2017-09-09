#![allow(unused_doc_comment)]

extern crate bcrypt;
#[macro_use]
extern crate cpython;
#[macro_use]
extern crate diesel;
#[macro_use]
extern crate diesel_codegen;
extern crate dotenv;
#[macro_use]
extern crate error_chain;
#[macro_use]
extern crate lazy_static;
extern crate r2d2;
extern crate r2d2_diesel;
extern crate redis;
extern crate x11;

mod utils;
mod users;
mod schema;
mod errors;

#[cfg(test)]
mod tests;

use cpython::Python;
use diesel::PgConnection;
use r2d2_diesel::ConnectionManager;
use std::env;
use redis::Commands;

lazy_static! {
    pub static ref DB_POOL: r2d2::Pool<ConnectionManager<PgConnection>> = {
        dotenv::dotenv().expect("Can't load the .env file");
        let config = r2d2::Config::default();
        let manager = ConnectionManager::<PgConnection>::new(
            if env::var("TEST_ENIBAR").is_ok() {
                "postgres://enibar@127.0.0.1:2356/enibar".to_owned()
            }
            else {
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
        );

        r2d2::Pool::new(config, manager).expect("Failed to connect to psql")
    };
}

py_module_initializer!(rapi, initrapi, PyInit_rapi, |py, m| {
    m.add(py, "utils", utils::as_module(py))?;
    m.add(py, "users", users::as_module(py))?;
    Ok(())
});
