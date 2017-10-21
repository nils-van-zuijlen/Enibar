use super::schema::*;
use panels::models::*;
use model::Model;

#[test]
fn add_panel() {
    let conn = connection();

    let panel = Panel::add(&conn, "coucou").unwrap();
    assert_eq!(panel.name, "coucou".to_owned());
    assert_eq!(panel.hidden, false);

    let panel = Panel::add(&conn, "coucou2").unwrap();
    assert_eq!(panel.name, "coucou2".to_owned());
    assert_eq!(panel.hidden, false);

    assert!(Panel::add(&conn, "coucou").is_err());
    assert!(Panel::add(&conn, "coucou2").is_err());
    assert!(Panel::add(&conn, " ").is_err());
    assert!(Panel::add(&conn, "").is_err());
}
#[test]
fn remove_panel() {
    let conn = connection();
    let panel = Panel::add(&conn, "coucou").unwrap();
    assert!(Panel::get(&conn, "coucou").is_ok());
    assert!(panel.delete(&conn).is_ok());
    assert!(Panel::get(&conn, "coucou").is_err());
}

#[test]
fn save_panel() {
    let conn = connection();
    let mut panel = Panel::add(&conn, "coucou").unwrap();
    panel.name = "coucou2".into();
    panel.hidden = true;
    let panel = panel.save(&conn).unwrap();
    assert_eq!(panel.name, "coucou2".to_owned());
    assert_eq!(panel.hidden, true);
}
