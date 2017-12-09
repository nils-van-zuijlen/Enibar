use super::schema::*;
use categories::models::*;
use model::Model;

#[test]
fn add_category() {
    let conn = connection();

    let category = Category::add(&conn, "coucou").unwrap();
    assert_eq!(category.name, "coucou".to_owned());
    assert_eq!(category.color, "#FFFFFF".to_owned());
    assert_eq!(category.alcoholic, false);

    let category = Category::add(&conn, "coucou2").unwrap();
    assert_eq!(category.name, "coucou2".to_owned());
    assert_eq!(category.color, "#FFFFFF".to_owned());
    assert_eq!(category.alcoholic, false);

    assert!(Category::add(&conn, "coucou").is_err());
    assert!(Category::add(&conn, "coucou2").is_err());
    assert!(Category::add(&conn, " ").is_err());
    assert!(Category::add(&conn, "").is_err());
}
#[test]
fn remove_category() {
    let conn = connection();
    let category = Category::add(&conn, "coucou").unwrap();
    assert!(Category::get(&conn, "coucou").is_ok());
    assert!(category.remove(&conn).is_ok());
    assert!(Category::get(&conn, "coucou").is_err());
}

#[test]
fn save_category() {
    let conn = connection();
    let mut category = Category::add(&conn, "coucou").unwrap();
    category.name = "coucou2".into();
    category.alcoholic = true;
    category.color = "#000000".into();
    let category = category.save(&conn).unwrap();
    assert_eq!(category.name, "coucou2".to_owned());
    assert_eq!(category.color, "#000000".to_owned());
    assert_eq!(category.alcoholic, true);
}
