use cpython::{ObjectProtocol, PyObject, Python, ToPyObject};
use BigDecimal;
use NaiveDate;
use chrono::Datelike;
use num_traits::ToPrimitive;

lazy_static! {
    pub static ref DATE: PyObject = {
        let gil = Python::acquire_gil();
        let py = gil.python();
        let datetime_module = py.import("datetime").expect("Can't import datetime");
        let date = datetime_module.get(py, "date").unwrap();
        date
    };
}

impl ToPyObject for BigDecimal {
    type ObjectType = PyObject;

    fn to_py_object(&self, py: Python) -> Self::ObjectType {

        return self.0.to_f64().to_py_object(py)
    }
}

impl ToPyObject for NaiveDate {
    type ObjectType = PyObject;

    fn to_py_object(&self, py: Python) -> Self::ObjectType {
        let date = |yyyy: i32, mm: u32, dd: u32| {
            DATE.call(py, (yyyy, mm, dd), None).unwrap()
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
