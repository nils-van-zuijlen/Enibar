use diesel::prelude::*;
use std::env;

pub fn connection() -> PgConnection {
    let res = connection_without_transaction();
    res.begin_test_transaction().unwrap();
    res
}

pub fn connection_without_transaction() -> PgConnection {
    let connection_url = match env::var("DATABASE_URL") {
        Ok(val) => val,
        Err(_) => "postgres://enibar@127.0.0.1:2356/enibar".to_owned(),
    };
    PgConnection::establish(&connection_url).unwrap()
}
