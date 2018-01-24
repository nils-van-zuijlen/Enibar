use schema::notes;
use validator::Validate;
use note_categories::models::NoteCategory;
use BigDecimal;
use ::NaiveDate;

#[derive(Debug, Queryable, AsChangeset, Identifiable, Model, Validate)]
#[table_name = "notes"]
pub struct Note {
    pub id: i64,
    pub nickname: String,
    pub lastname: String,
    pub firstname: String,
    pub mail: String,
    pub tel: String,
    pub birthdate: i32,
    pub promo: String,
    pub photo_path: Option<String>,
    pub note: BigDecimal,
    pub overdraft_date: Option<NaiveDate>,
    pub ecocups: i32,
    //pub last_agio: Option<NaiveDate>,
    pub mails_inscription: bool,
    pub stats_inscription: bool,
    pub agios_inscription: bool,
    pub tot_cons: BigDecimal,
    pub tot_refill: BigDecimal,
}

#[derive(Queryable, Debug)]
pub struct NoteCacheEntry {
    pub note: Note,
    pub categories: Vec<NoteCategory>,
    pub hidden: bool,
}

