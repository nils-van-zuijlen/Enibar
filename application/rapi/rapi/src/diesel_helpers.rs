use diesel::pg::Pg;
use diesel::sql_types::*;
use diesel::serialize::{self, ToSql};
use diesel::deserialize::{self, FromSql};
use bigdecimal;
use chrono;
use std::ops::Deref;
use std::io::Write;

macro_rules! diesel_wrapper {
    ($sql_type: ident -> $rust_type: ident ($real_type: path)) => {
        impl ToSql<$sql_type, Pg> for $rust_type {
            fn to_sql<W: Write>(
                &self,
                out: &mut serialize::Output<W, Pg>,
            ) -> serialize::Result {
                <$real_type as ToSql<$sql_type, Pg>>::to_sql(&self.0, out)
            }
        }

        impl FromSql<$sql_type, Pg> for $rust_type {
            fn from_sql(
                bytes: Option<&[u8]>
            ) -> deserialize::Result<Self> {
                Ok($rust_type(<$real_type as FromSql<$sql_type, Pg>>::from_sql(bytes)?))
            }
        }

        impl Deref for $rust_type {
            type Target = $real_type;

            fn deref(&self) -> &Self::Target {
                &self.0
            }
        }
    }
}

diesel_wrapper!(Numeric -> BigDecimal(bigdecimal::BigDecimal));
diesel_wrapper!(Date -> NaiveDate(chrono::NaiveDate));

#[derive(Debug, Clone)]
#[derive(AsExpression, FromSqlRow)]
#[sql_type="Numeric"]
pub struct BigDecimal(pub bigdecimal::BigDecimal);

#[derive(Debug, Clone)]
#[derive(AsExpression, FromSqlRow)]
#[sql_type="Date"]
pub struct NaiveDate(pub chrono::NaiveDate);
