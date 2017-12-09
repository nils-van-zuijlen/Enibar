use diesel::pg::Pg;
use diesel::types::*;
use diesel::row::Row;
use bigdecimal;
use chrono;
use std::ops::Deref;
use std::error::Error;
use std::io::Write;


macro_rules! diesel_wrapper {
    ($sql_type: ident -> $rust_type: ident ($real_type: path)) => {
        #[derive(Debug, Clone)]
        pub struct $rust_type(pub $real_type);

        expression_impls!($sql_type -> $rust_type);
        queryable_impls!($sql_type -> $rust_type);

        impl ToSql<$sql_type, Pg> for $rust_type {
            fn to_sql<W: Write>(
                &self,
                out: &mut ToSqlOutput<W, Pg>,
            ) -> Result<IsNull, Box<Error + Send + Sync>> {
                <$real_type as ToSql<$sql_type, Pg>>::to_sql(&self.0, out)
            }
        }

        impl FromSqlRow<$sql_type, Pg> for $rust_type {
            fn build_from_row<T: Row<Pg>>(row: &mut T) -> Result<Self, Box<Error + Send + Sync>> {
                Ok($rust_type(
                    <$real_type as FromSqlRow<$sql_type, Pg>>::build_from_row(row)?,
                ))
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
