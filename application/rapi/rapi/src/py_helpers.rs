use cpython::{ObjectProtocol, PyObject, PyString, Python, ToPyObject};
use BigDecimal;

impl ToPyObject for BigDecimal {
    type ObjectType = PyObject;

    fn to_py_object(&self, py: Python) -> Self::ObjectType {
        let decimal_module = py.import("decimal").expect("Can't import decimal");
        let decimal = decimal_module.get(py, "Decimal").unwrap();

        let decimal = |object: &PyString| {
            return decimal.call(py, (object,), None).unwrap();
        };

        return decimal(&format!("{}", self.0).into_py_object(py));
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
