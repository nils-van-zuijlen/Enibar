pub mod models;
mod py;

use self::py::*;
pub use self::models::*;
use schema::notes;
use cpython::{PyModule, Python};
use diesel::prelude::*;
use errors::*;

impl Note {
    pub fn get(conn: &PgConnection, name: &str) -> Result<Self> {
        notes::table.filter(notes::nickname.eq(name)).first(conn).map_err(|e| e.into())
    }
}

fn get_cache(conn: &PgConnection) -> Result<Vec<NoteCacheEntry>> {
    use schema::notes_cache::dsl::*;

    notes_cache.select( ( (id, nickname, lastname, firstname, mail, tel, birthdate, promo,
                           photo_path, note, overdraft_date, ecocups, mails_inscription,
                           stats_inscription, agios_inscription, tot_cons, tot_refill, ),
                           categories, hidden,)).load(conn).map_err(|e| e.into())
}

fn get_note_cache(conn: &PgConnection, note_nick: &str) -> Result<NoteCacheEntry> {
    use schema::notes_cache::dsl::*;

    notes_cache.select( ( (id, nickname, lastname, firstname, mail, tel, birthdate, promo,
                           photo_path, note, overdraft_date, ecocups, mails_inscription,
                           stats_inscription, agios_inscription, tot_cons, tot_refill, ),
                           categories, hidden,)).filter(nickname.eq(note_nick)).first(conn).map_err(|e| e.into())
}

pub fn as_module(py: Python) -> PyModule {
    let module = PyModule::new(py, "notes").unwrap();
    let _ = module.add(py, "remove", py_fn!(py, py_remove(id: Vec<String>)));
    let _ = module.add(py, "get_cache", py_fn!(py, py_get_cache()));
    let _ = module.add(py, "get_note_cache", py_fn!(py, py_get_note_cache(note: String)));

    module
}

