use cpython::{PyBool, PyDict, PyList, PyObject, PyResult, Python, PythonObject, ToPyObject};
use cpython::PythonObjectWithCheckedDowncast;
use panels::models::Panel;
use model::Model;
use diesel::*;
use std::collections::HashMap;

pub fn py_add(py: Python, name: &str) -> PyResult<PyObject> {
    let conn = ::DB_POOL.get().unwrap();

    let panel = Panel::add(&*conn, name);
    match panel {
        Ok(p) => Ok(p.id.to_py_object(py).into_object()),
        Err(_) => Ok(py.None()),
    }
}

pub fn py_remove(py: Python, name: &str) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    let panel = Panel::get(&*conn, name);
    if let Ok(p) = panel {
        if p.remove(&*conn).is_ok() {
            return Ok(py.True());
        }
    }

    Ok(py.False())
}

pub fn py_hide(py: Python, name: &str) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    let panel = Panel::get(&*conn, name);
    if let Ok(mut p) = panel {
        p.hidden = true;

        if p.save(&*conn).is_ok() {
            return Ok(py.False());
        }
    }

    Ok(py.False())
}

pub fn py_show(py: Python, name: &str) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    let panel = Panel::get(&*conn, name);
    if let Ok(mut p) = panel {
        p.hidden = false;

        if p.save(&*conn).is_ok() {
            return Ok(py.False());
        }
    }

    Ok(py.False())
}

pub fn py_add_products(py: Python, id: i32, product_ids: Vec<i32>) -> PyResult<PyBool> {
    // XXX: Since the python API is so bad, I'm allowing this function to do a SQL request without
    // passing by the rust RAPI for performances reasons.
    use schema::products;
    let conn = ::DB_POOL.get().unwrap();

    let panel = Panel::get_by_id(&*conn, id);
    if let Ok(p) = panel {
        if let Ok(products) = products::table
            .filter(products::id.eq_any(product_ids))
            .load(&*conn)
        {
            return Ok(PyBool::get(py, p.add_products(&*conn, &products).is_ok()));
        }
    }

    Ok(py.False())
}

pub fn py_remove_products(py: Python, id: i32, product_ids: Vec<i32>) -> PyResult<PyBool> {
    use schema::products;
    let conn = ::DB_POOL.get().unwrap();

    let panel = Panel::get_by_id(&*conn, id);
    if let Ok(p) = panel {
        if let Ok(products) = products::table
            .filter(products::id.eq_any(product_ids))
            .load(&*conn)
        {
            return Ok(PyBool::get(
                py,
                p.remove_products(&*conn, &products).is_ok(),
            ));
        }
    }

    Ok(py.False())
}

pub fn py_get_content(py: Python, id: i32) -> PyResult<PyList> {
    let conn = ::DB_POOL.get().unwrap();

    let mut content = vec![];
    let panel = Panel::get_by_id(&*conn, id);
    if let Ok(p) = panel {
        for c in p.content(&*conn).unwrap() {
            content.push(
                dict!(py,
               {"panel_id" => p.id,
                "product_id" => c.product.id,
                "product_name" => c.product.name,
                "product_percentage" => c.product.percentage,
                "category_id" => c.category.id,
                "category_name" => c.category.name}
            ).unwrap()
                    .into_object(),
            );
        }
    }

    Ok(PyList::new(py, &content))
}

pub fn py_get_all(py: Python) -> PyResult<PyDict> {
    let conn = ::DB_POOL.get().unwrap();
    let panels = Panel::get_all(&*conn).unwrap();
    let mut m = HashMap::new();

    for ref entry in &panels {
        let mut panel = m.entry(&entry.panel_name).or_insert_with(HashMap::new);
        let mut cat = panel.entry(&entry.category_name).or_insert_with( ||
            dict!(py, { "category_id" => entry.category_id,
                        "alcoholic" => entry.category_alcoholic,
                        "color" => &entry.category_color }).unwrap()
        );

        let mut products = match cat.get_item(py, "products") {
            Some(c) => PyDict::downcast_from(py, c).unwrap(),
            None => PyDict::new(py),
        };
        cat.set_item(py, "products", &products)?;
        for line in &entry.products {
            let prod = match products.get_item(py, &line.product_name) {
                Some(c) => PyDict::downcast_from(py, c).unwrap(),
                None => PyDict::new(py),
            };

            let prices = match prod.get_item(py, "prices") {
                Some(c) => PyDict::downcast_from(py, c).unwrap(),
                None => PyDict::new(py),
            };

            prices.set_item(py, &line.price_label, &line.price)?;
            prod.set_item(py, "prices", prices)?;
            prod.set_item(py, "product_id", &line.product_id)?;
            prod.set_item(py, "percentage", &line.percentage)?;
            products.set_item(py, &line.product_name, prod)?;
        }
    }

    Ok(m.into_py_object(py))
}
