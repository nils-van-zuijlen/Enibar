use super::schema::*;
use note_categories::models::*;
use model::Model;

#[test]
fn add_note_category() {
    let conn = connection();

    let category = NoteCategory::add(&conn, "coucou").unwrap();
    assert_eq!(category.name, "coucou".to_owned());
    assert_eq!(category.hidden, false);
    assert_eq!(category.protected, false);

    let category = NoteCategory::add(&conn, "coucou2").unwrap();
    assert_eq!(category.name, "coucou2".to_owned());
    assert_eq!(category.hidden, false);
    assert_eq!(category.protected, false);

    assert!(NoteCategory::add(&conn, "coucou").is_err());
    assert!(NoteCategory::add(&conn, "coucou2").is_err());
    assert!(NoteCategory::add(&conn, " ").is_err());
    assert!(NoteCategory::add(&conn, "").is_err());
}

#[test]
fn remove_note_category() {
    let conn = connection();
    let category = NoteCategory::add(&conn, "coucou").unwrap();
    assert!(NoteCategory::get(&conn, "coucou").is_ok());
    assert!(category.remove(&conn).is_ok());
    assert!(NoteCategory::get(&conn, "coucou").is_err());

    let mut category = NoteCategory::add(&conn, "coucou").unwrap();
    category.protected = true;
    let category = category.save(&conn).unwrap();
    assert!(NoteCategory::get(&conn, "coucou").is_ok());
    assert!(category.remove(&conn).is_ok());
    assert!(NoteCategory::get(&conn, "coucou").is_ok());
}

#[test]
fn save_category() {
    let conn = connection();
    let mut category = NoteCategory::add(&conn, "coucou").unwrap();
    category.name = "coucou2".into();
    category.hidden = true;
    category.protected = true;
    let category = category.save(&conn).unwrap();
    assert_eq!(category.name, "coucou2".to_owned());
    assert_eq!(category.hidden, true);
    assert_eq!(category.protected, true);
}
