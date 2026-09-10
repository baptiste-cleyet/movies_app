import Eye from "./vendor/lucide/icons/eye.js";
import Search from "./vendor/lucide/icons/search.js";
import ArrowDownWideNarrow from "./vendor/lucide/icons/arrow-down-wide-narrow.js";
import ArrowUpNarrowWide from "./vendor/lucide/icons/arrow-up-narrow-wide.js";
import FilePlus2 from "./vendor/lucide/icons/file-plus-2.js";
import LayoutGrid from "./vendor/lucide/icons/layout-grid.js";
import Moon from "./vendor/lucide/icons/moon.js";
import Sun from "./vendor/lucide/icons/sun.js";
import Trash2 from "./vendor/lucide/icons/trash-2.js";
import Pencil from "./vendor/lucide/icons/pencil.js";
import SquareArrowOutUpRight from "./vendor/lucide/icons/square-arrow-out-up-right.js";
import Calendar from "./vendor/lucide/icons/calendar.js";
import Type from "./vendor/lucide/icons/type.js";
import Star from "./vendor/lucide/icons/star.js";
import CalendarClock from "./vendor/lucide/icons/calendar-clock.js";
import BookOpen from "./vendor/lucide/icons/book-open.js";
import MessageSquare from "./vendor/lucide/icons/message-square.js";
import CircleChevronDown from "./vendor/lucide/icons/circle-chevron-down.js";
import SquareMenu from "./vendor/lucide/icons/square-menu.js";
import replaceElement from "./vendor/lucide/replaceElement.js";

export const icons = {
    Eye,
    Search,
    ArrowDownWideNarrow,
    ArrowUpNarrowWide,
    FilePlus2,
    LayoutGrid,
    Moon,
    Sun,
    Trash2,
    Pencil,
    SquareArrowOutUpRight,
    Calendar,
    Type,
    Star,
    CalendarClock,
    BookOpen,
    MessageSquare,
    CircleChevronDown,
    SquareMenu,
};

export const createIcons = ({ icons: iconSet = icons, nameAttr = "data-lucide", attrs = {} } = {}) => {
    if (!Object.values(iconSet).length) {
        throw new Error("Please provide an icons object.");
    }
    if (typeof document === "undefined") {
        throw new Error("`createIcons()` only works in a browser environment.");
    }
    const elementsToReplace = document.querySelectorAll(`[${nameAttr}]`);
    Array.from(elementsToReplace).forEach((element) => replaceElement(element, { nameAttr, icons: iconSet, attrs }));
    if (nameAttr === "data-lucide") {
        const deprecatedElements = document.querySelectorAll("[icon-name]");
        if (deprecatedElements.length > 0) {
            Array.from(deprecatedElements).forEach((element) => replaceElement(element, { nameAttr: "icon-name", icons: iconSet, attrs }));
        }
    }
};
