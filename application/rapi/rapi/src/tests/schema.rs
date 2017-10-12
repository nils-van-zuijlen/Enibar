use diesel::prelude::*;

pub fn connection() -> PgConnection {
    let res = connection_without_transaction();
    res.begin_test_transaction().unwrap();
    res
}

pub fn connection_without_transaction() -> PgConnection {
    let connection_url = "postgres://enibar@127.0.0.1:2356/enibar";
    PgConnection::establish(&connection_url).unwrap()
}
