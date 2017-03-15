use gtk;
use gtk::prelude::*;
use gtk::{Builder, Button, Entry, Window, WidgetExt, ComboBox, ListStore};
use gdk::enums::key;
use admins::*;
use std::cell::RefCell;
use std::rc::Rc;
use gui::utils::*;


pub struct PasswordPrompt {
    pub users_cbox: ComboBox,
    pub password_input: Entry,
    pub is_authorized: bool,
    pub is_error: bool,
}


impl PasswordPrompt {
    pub fn new(manage_notes: bool, manage_users: bool, manage_products: bool) -> Rc<RefCell<Self>> {
        let glade_src = include_str!("ui/password_prompt.glade");
        let builder = Builder::new_from_string(glade_src);

        let window: Window = builder.get_object("window").unwrap();
        let users_cbox: ComboBox = builder.get_object("users_cbox").unwrap();
        let password_input: Entry = builder.get_object("password_input").unwrap();
        let login_button: Button = builder.get_object("login_button").unwrap();
        let cancel_button: Button = builder.get_object("cancel_button").unwrap();

        let user_list = ListStore::new(&[String::static_type(), String::static_type()]);
        for user in Admin::get_filtered(manage_notes, manage_users, manage_products) {
            user_list.insert_with_values(Some(0), &[0], &[&user.login]);
        }

        setup_combobox(&users_cbox, &user_list, 0, 0);

        let prompt = Rc::new(RefCell::new(PasswordPrompt { is_authorized: false, users_cbox: users_cbox, password_input: password_input, is_error: false }));

        window.connect_key_press_event(|w, e| {
            match e.get_keyval() {
                key::Escape => {
                    WidgetExt::destroy(w);
                    gtk::main_quit();
                },
                _ => {},
            }

            Inhibit(false)
        });

        cancel_button.connect_clicked(|b| {
            let w = b.get_toplevel().unwrap();
            WidgetExt::destroy(&w);
            gtk::main_quit();
        });

        let closure_prompt = prompt.clone();
        login_button.connect_clicked(move |b| {
            let mut prompt = closure_prompt.borrow_mut();
            let username = prompt.users_cbox.get_active_id().unwrap();
            let password = prompt.password_input.get_text().unwrap();
            prompt.is_authorized = Admin::is_authorized(&username, &password);
            prompt.is_error = true;

            let w = b.get_toplevel().unwrap();
            WidgetExt::destroy(&w);
            gtk::main_quit();
        });

        window.connect_delete_event(|_, _| {
            gtk::main_quit();
            Inhibit(false)
        });

        let closure_prompt = prompt.clone();
        let p = prompt.clone();
        p.borrow().password_input.connect_activate(move |i| {
            let mut prompt = closure_prompt.borrow_mut();
            let username = prompt.users_cbox.get_active_id().unwrap();
            let password = prompt.password_input.get_text().unwrap();
            prompt.is_authorized = Admin::is_authorized(&username, &password);
            prompt.is_error = true;

            let w = i.get_toplevel().unwrap();
            WidgetExt::destroy(&w);
            gtk::main_quit();
        });

        window.show_all();

        prompt.clone()
    }
}
