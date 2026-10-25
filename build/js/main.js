import Alpine from "alpinejs";
import { showServerMessages } from "./ui";
import "./inline-edit";
import "./emoji";
import "./search";
import "./board";
import "./home";
import "./settings";
import "./theme";

window.Alpine = Alpine;
Alpine.start();
showServerMessages();
