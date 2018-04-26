use gtk::{self, prelude::*};
use gtk::Orientation::{Horizontal, Vertical};
use gtk::OrientableExt;
use relm::{Component, ContainerWidget, Relm, Update, Widget};

use self::WinMsg::*;
use widgets::text_input::{TextInputMsg::*, *};
use rapi;
use rapi::users::User;


#[derive(Msg, Clone)]
pub enum WinMsg {
    Cancel,
    Quit,
    Valid,
    UsernameChanged(String),
    PasswordChanged(String),
    #[cfg(test)] GetModel,
    #[cfg(test)] RecvModel(WinModel),
}


#[derive(Clone)]
pub struct WinModel {
    relm: Relm<Win>,
    pub ok: bool,
    username: String,
    password: String,
}

relm_widget! {
    impl Widget for Win {
        fn model(relm: &Relm<Self>, _: ()) -> WinModel {
            WinModel {
                relm: relm.clone(),
                username: "".into(),
                password: "".into(),
                ok: false,
            }
        }

        fn update(&mut self, event: WinMsg) {
            println!("{:?}", ::std::mem::discriminant(&event));
            match event {
                Cancel | Quit => gtk::main_quit(),
                Valid => {
                    self.model.ok = true;
                    eprintln!("COUCOUCOUCOU");
                    let conn = rapi::DB_POOL.get().unwrap();
                    let user = User::get(&*conn, &self.model.username);
                    eprintln!("{:?}", user);
                    if let Ok(user) = user {
                        self.model.ok = user.is_authorized(&self.model.password).unwrap_or(false);
                    }
                },
                UsernameChanged(username) => self.model.username = username,
                PasswordChanged(password) => self.model.password = password,
                #[cfg(test)]
                GetModel => {
                    self.model.relm.stream().emit(RecvModel(self.model.clone()));
                }
                #[cfg(test)]
                RecvModel(_) => {}
            }
        }

        view! {
            gtk::Window {
                gtk::Box {
                    orientation: Vertical,
                    #[name="login_input"]
                    TextInput {
                        SetLabel: "Login".to_string(),
                        Change(ref login) => WinMsg::UsernameChanged(login.clone()),
                    },
                    #[name="password_input"]
                    TextInput {
                        SetLabel: "Password".to_string(),
                        Change(ref password) => WinMsg::PasswordChanged(password.clone()),
                    },
                    gtk::Box {
                        orientation: Horizontal,
                        #[name="cancel_button"]
                        gtk::Button {
                            clicked => WinMsg::Cancel,
                            label: "Cancel",
                        },
                        #[name="validate_button"]
                        gtk::Button {
                            clicked => WinMsg::Valid,
                            label: "Cancel",
                        },
                    },
                },
                delete_event(_, _) => (WinMsg::Quit, Inhibit(false)),
            }
        }
    }
}

