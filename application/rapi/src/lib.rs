#[macro_use] extern crate cpython;
#[macro_use] extern crate diesel_codegen;
#[macro_use] extern crate diesel;
extern crate bcrypt;
extern crate dotenv;
extern crate x11;
extern crate chrono;
extern crate r2d2;
extern crate r2d2_diesel;
#[macro_use] extern crate lazy_static;
extern crate gtk;
extern crate gdk;

use diesel::pg::PgConnection;
use r2d2_diesel::ConnectionManager;
use dotenv::dotenv;
use std::env;


mod utils;
mod schema;
mod admins;
mod gui;


lazy_static! {
    pub static ref DB_POOL: r2d2::Pool<ConnectionManager<PgConnection>> = {
        dotenv().expect("Can't load the .env file");
        let config = r2d2::Config::default();
        let manager = ConnectionManager::<PgConnection>::new(
            env::var("DATABASE_URL").expect("DATABASE_URL not in env vars")
        );

        r2d2::Pool::new(config, manager).expect("Failed to connect to psql")
    };
}

py_module_initializer!(rapi, initrapi, PyInit_rapi, |py, m| {
    m.add(py, "utils", utils::as_module(py))?;
    m.add(py, "gui", gui::as_module(py))?;
    Ok(())
});
