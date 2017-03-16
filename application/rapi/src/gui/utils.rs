use gtk;
use gtk::prelude::*;
use std::rc::Rc;
use std::cell::RefCell;


pub fn setup_combobox(cb: &gtk::ComboBox, model: &gtk::ListStore, id_column: i32, text_column: i32) {
    cb.set_model(Some(model));

    cb.set_id_column(id_column);
    cb.set_entry_text_column(text_column);

    let cell = gtk::CellRendererText::new();
    cb.pack_start(&cell, true);
    cb.add_attribute(&cell, "text", text_column);
    //cb.set_active(0);

    let string_typed  = Rc::new(RefCell::new(String::new()));
    let last_char_typed_time = Rc::new(RefCell::new(0));

    cb.connect_key_press_event(move |o, e| {
        let key = e.get_keyval() as u8 as char;
        let time = e.get_time();

        let mut string_typed = string_typed.borrow_mut();
        let mut last_char_typed_time = last_char_typed_time.borrow_mut();

        if time - *last_char_typed_time < 500 || string_typed.is_empty() {
            *string_typed += &format!("{}", key);
        }
        else {
            *string_typed = format!("{}", key);
        }
        *last_char_typed_time = time;
        *string_typed = string_typed.to_lowercase();


        let current_string = o.get_active_id().unwrap().to_lowercase();
        let model = o.get_model().unwrap();

        let item = model.get_iter_first().unwrap();
        let mut selected = None;

        'main: loop {
            // If the current selected item begins with the key typed
            if current_string.starts_with(&*string_typed) {
                // Advance the iterator to the current selected item + 1
                loop {
                    let string: String = model.get_value(&item, 0).get().unwrap();
                    let string = string.to_lowercase();
                    if current_string == string {
                        if !model.iter_next(&item) {
                            break 'main;
                        }
                        break;
                    }
                    else if !model.iter_next(&item) {
                        break 'main;
                    }
                }
            }

            let string: String = model.get_value(&item, 0).get().unwrap();
            let string = string.to_lowercase();

            if string.starts_with(&*string_typed) {
                selected = Some(&item);
                break;
            }

            if !model.iter_next(&item) {
                break;
            }
        }

        if selected.is_some() {
            o.set_active_iter(selected);
        }

        Inhibit(false)
    });
}


