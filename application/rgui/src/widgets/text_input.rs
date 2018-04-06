use gtk::{self, Button, ButtonExt, ContainerExt, EditableSignals, Entry, EntryExt, Inhibit, Label,
          LabelExt, WidgetExt, Window, WindowType};
use gtk::Orientation::{Horizontal, Vertical};
use gtk::OrientableExt;
use relm::{Component, ContainerWidget, Relm, Update, Widget};

#[derive(Clone)]
pub struct TextInputModel {
}

#[derive(Msg, Clone)]
pub enum TextInputMsg {
    Change(String),
    SetLabel(String),
}

use self::TextInputMsg::*;

relm_widget! {
    impl Widget for TextInput {
        fn model() -> TextInputModel {
            TextInputModel {
            }
        }

        fn update(&mut self, event: TextInputMsg) {
            match event {
                Change(_) => { },
                SetLabel(label) => {
                    self.label.set_label(&label);
                },
            }
        }

        view! {
            gtk::Box {
                orientation: Vertical,
                #[name = "label"]
                gtk::Label {
                },
                #[name="input"]
                gtk::Entry {
                    name: "input",
                    changed(value) => Change(value.get_text().unwrap()),
                },
            }
        }
    }
}
