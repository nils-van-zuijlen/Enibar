use cpython::{ObjectProtocol, PyObject, PyString, Python, ToPyObject};
use BigDecimal;
use NaiveDate;
use chrono::Datelike;
use std::sync::{Once, ONCE_INIT};

static DATE_ONCE: Once = ONCE_INIT;
static mut DATE: Option<Box<PyObject>> = None;

static DECIMAL_ONCE: Once = ONCE_INIT;
static mut DECIMAL: Option<Box<PyObject>> = None;

impl ToPyObject for BigDecimal {
    type ObjectType = PyObject;

    fn to_py_object(&self, py: Python) -> Self::ObjectType {
        DECIMAL_ONCE.call_once(|| {
            let decimal_module = py.import("decimal").expect("Can't import decimal");
            let decimal = decimal_module.get(py, "Decimal").unwrap();
            unsafe {
                DECIMAL = Some(Box::new(decimal));
            }
        });

        let decimal = |object: &PyString| {
            unsafe {
                match DECIMAL {
                    Some(ref decimal) => decimal.call(py, (object,), None).unwrap(),
                    None => unreachable!(),
                }
            }
        };

        return decimal(&format!("{}", self.0).into_py_object(py));
    }
}

impl ToPyObject for NaiveDate {
    type ObjectType = PyObject;

    fn to_py_object(&self, py: Python) -> Self::ObjectType {
        DATE_ONCE.call_once(|| {
            let datetime_module = py.import("datetime").expect("Can't import datetime");
            let date = datetime_module.get(py, "date").unwrap();
            unsafe {
                DATE = Some(Box::new(date));
            }
        });

        let date = |yyyy: i32, mm: u32, dd: u32| {
            unsafe {
                match DATE {
                    Some(ref date) => date.call(py, (yyyy, mm, dd), None).unwrap(),
                    None => unreachable!(),
                }
            }
        };


        date(self.year(), self.month(), self.day()).into_py_object(py)
    }
}

#[macro_export]
macro_rules! dict {
    ($py: ident, { $($key: expr => $value: expr),+ }) => {
        {
        let d = ::cpython::PyDict::new($py);
        $(d.set_item($py, $key, $value)?;)+
        let ret: ::cpython::PyResult<::cpython::PyDict> = Ok(d);
        ret
        }
    }
}
