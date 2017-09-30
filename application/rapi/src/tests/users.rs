use super::schema::*;
use users::models::*;

#[test]
fn add_user() {
    let conn = connection();

    let user = User::add(&conn, "coucou", "coucou").unwrap();
    // Test that the password has been hashed and replace the password
    assert!(user.password.starts_with('$'));
    assert_eq!(user.login, "coucou");

    let user = User::add(&conn, "coucou2", "coucou2").unwrap();
    assert!(user.password.starts_with('$'));
    assert_eq!(user.login, "coucou2");

    let user = User::add(&conn, "coucou3", "coucou2").unwrap();
    assert!(user.password.starts_with('$'));
    assert_eq!(user.login, "coucou3");

    assert!(User::add(&conn, "coucou", "coucou").is_err());
    assert!(User::add(&conn, "coucou", "coucou2").is_err());
    assert!(User::add(&conn, "", "coucou").is_err());
    assert!(User::add(&conn, "coucou", "").is_err());
}

#[test]
fn check_password() {
    let conn = connection();

    let user = User::add(&conn, "coucou", "coucou").unwrap();
    assert!(user.is_authorized("coucou").unwrap());
    assert!(!user.is_authorized("coucou2").unwrap());
    assert!(!user.is_authorized("").unwrap());
}

#[test]
fn change_password() {
    let conn = connection();

    let user = User::add(&conn, "coucou", "coucou").unwrap();
    assert!(user.is_authorized("coucou").unwrap());
    let user = user.change_password(&conn, "test").unwrap();
    assert!(!user.is_authorized("coucou").unwrap());
    assert!(user.is_authorized("test").unwrap());
}

#[test]
fn remove_user() {
    let conn = connection();
    let user = User::add(&conn, "coucou", "coucou").unwrap();
    assert!(User::get(&conn, "coucou").is_ok());
    assert!(user.remove(&conn).is_ok());
    assert!(User::get(&conn, "coucou").is_err());
}
