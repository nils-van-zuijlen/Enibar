use chrono::{NaiveDate, Utc};
use bigdecimal::BigDecimal;

#[derive(Debug, Queryable)]
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
    pub last_agio: Option<NaiveDate>,
    pub mails_inscription: bool,
    pub stats_inscription: bool,
    pub agios_inscription: bool,
}

