use cpython::{Python, PyResult, PyDict, ToPyObject};
use notes::models::Note;

impl ToPyObject for Note {
    type ObjectType = PyDict;

    fn to_py_object(&self, py: Python) -> Self::ObjectType {
        let d = PyDict::new(py);
        d.set_item(py, "id", self.id);
        d.set_item(py, "nickname", self.nickname.clone());
        d.set_item(py, "lastname", self.lastname.clone());
        d.set_item(py, "firstname", self.firstname.clone());
        d.set_item(py, "mail", self.mail.clone());
        d.set_item(py, "tel", self.tel.clone());
        d.set_item(py, "birthdate", self.birthdate);
        d.set_item(py, "promo", self.promo.clone());
        d.set_item(py, "photo_path", self.photo_path.clone());
        //d.set_item(py, "note", self.note);
        //d.set_item(py, "overdraft_date", self.overdraft_date);
        d.set_item(py, "ecocups", self.ecocups);
        //d.set_item(py, "last_agio", self.last_agio);
        d.set_item(py, "mails_inscription", self.mails_inscription);
        d.set_item(py, "stats_inscription", self.stats_inscription);
        d.set_item(py, "agios_inscription", self.agios_inscription);
        d
    }
}

pub fn py_get_cache(py: Python) -> PyResult<PyDict> {
    let conn = ::DB_POOL.get().unwrap();

    let cache = PyDict::new(py);

    let notes = Note::all(&*conn).unwrap();
    for note in notes {
        let d = note.to_py_object(py);
        d.set_item(py, "tot_cons", 0);
        d.set_item(py, "tot_refill", 0);
        d.set_item(py, "categories", vec!["a".to_owned()]);
        d.set_item(py, "hidden", false);
        cache.set_item(py, note.nickname.clone(), note)?;
    }

    Ok(cache)
}
