use cpython::{FromPyObject, ObjectProtocol, PyObject, PyResult, PyString, Python, PythonObject,
              ToPyObject};
use BigDecimal;
use num_traits::cast::ToPrimitive;
use bigdecimal;

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
