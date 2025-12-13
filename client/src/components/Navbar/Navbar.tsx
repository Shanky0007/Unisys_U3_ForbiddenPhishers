"use client";

import { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import type { RootState } from "@/store/store";
import { logout } from "@/store/auth/authSlice";
import { motion } from "framer-motion";
import { Menu, X, User, LogOut, ChevronDown, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from "@/components/ui/collapsible";

const navGroups = [
    {
        label: "Interview & Practice",
        links: [
            { href: "/interview", label: "Mock Interview" },
            { href: "/interview-help", label: "Interview AI Assistant" },
            { href: "/interview-questions", label: "DSA Questions" },
            { href: "/your-interviews", label: "Your Interviews" },
        ],
    },
    {
        label: "Learning & Tools",
        links: [
            { href: "/roadmaps", label: "Roadmap" },
            { href: "/Whiteboard", label: "Whiteboard" },
            { href: "/pdf-chat", label: "PDF Chat" },
            { href: "/resume-evaluate", label: "Resume Evaluate" },
        ],
    },
    {
        label: "Assessment",
        links: [
            { href: "/quiz", label: "Quiz" },
            { href: "/quiz-history", label: "Quiz History" },
            { href: "/insights", label: "Insights" },
        ],
    },
];

const Navbar = () => {
    const [isOpen, setIsOpen] = useState<boolean>(false);
    const [activeLink, setActiveLink] = useState<string>("/");
    const [scrolled, setScrolled] = useState<boolean>(false);
    const [openGroups, setOpenGroups] = useState<{ [key: string]: boolean }>({});

    const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn);
    const user = useSelector((state: RootState) => state.auth.user);
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        setActiveLink(location.pathname);
    }, [location]);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 20);
        };

        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const handleLogout = () => {
        dispatch(logout());
        navigate("/login");
    };

    const toggleGroup = (groupLabel: string) => {
        setOpenGroups((prev) => ({
            ...prev,
            [groupLabel]: !prev[groupLabel],
        }));
    };

    const isGroupActive = (group: (typeof navGroups)[0]) => {
        return group.links.some((link) => link.href === activeLink);
    };

    const NavLink = ({
        href,
        label,
        isActive,
        onClick,
    }: {
        href: string;
        label: string;
        isActive: boolean;
        onClick: () => void;
    }) => (
        <Link
            to={href}
            className="relative px-4 py-2 group overflow-hidden rounded-lg"
            onClick={onClick}
        >
            <motion.span
                className={`relative z-10 text-sm font-medium transition-colors duration-300 ${isActive ? "text-primary-foreground" : "text-muted-foreground group-hover:text-foreground"
                    }`}
            >
                {label}
            </motion.span>

            {isActive && (
                <motion.div
                    layoutId="nav-pill"
                    className="absolute inset-0 bg-primary rounded-lg"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ type: "spring", stiffness: 380, damping: 30 }}
                />
            )}

            <motion.div
                className="absolute inset-0 bg-muted rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                style={{ zIndex: -1 }}
            />
        </Link>
    );

    const NavDropdown = ({ group }: { group: (typeof navGroups)[0] }) => {
        const isActive = isGroupActive(group);

        return (
            <DropdownMenu>
                <DropdownMenuTrigger asChild>
                    <button className="relative px-4 py-2 group overflow-hidden rounded-lg flex items-center space-x-1">
                        <motion.span
                            className={`relative z-10 text-sm font-medium transition-colors duration-300 ${isActive
                                    ? "text-primary-foreground"
                                    : "text-muted-foreground group-hover:text-foreground"
                                }`}
                        >
                            {group.label}
                        </motion.span>
                        <ChevronDown
                            className={`h-4 w-4 transition-colors duration-300 ${isActive
                                    ? "text-primary-foreground"
                                    : "text-muted-foreground group-hover:text-foreground"
                                }`}
                        />

                        {isActive && (
                            <motion.div
                                layoutId="nav-pill"
                                className="absolute inset-0 bg-primary rounded-lg"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ type: "spring", stiffness: 380, damping: 30 }}
                            />
                        )}

                        <motion.div
                            className="absolute inset-0 bg-muted rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                            style={{ zIndex: -1 }}
                        />
                    </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                    align="start"
                    className="w-56 overflow-hidden rounded-xl p-1 shadow-lg border-border"
                >
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.2 }}
                    >
                        {group.links.map((link) => (
                            <DropdownMenuItem
                                key={link.href}
                                onClick={() => {
                                    setActiveLink(link.href);
                                    navigate(link.href);
                                }}
                                className={`cursor-pointer rounded-lg transition-colors duration-150 py-2 ${activeLink === link.href
                                        ? "bg-primary text-primary-foreground"
                                        : "hover:bg-muted"
                                    }`}
                            >
                                <span>{link.label}</span>
                            </DropdownMenuItem>
                        ))}
                    </motion.div>
                </DropdownMenuContent>
            </DropdownMenu>
        );
    };

    const MobileNavLink = ({
        href,
        label,
        isActive,
        onClick,
    }: {
        href: string;
        label: string;
        isActive: boolean;
        onClick: () => void;
    }) => (
        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Link
                to={href}
                onClick={onClick}
                className={`block px-4 py-3 rounded-xl text-base font-medium transition-all duration-200 ${isActive
                        ? "bg-primary text-primary-foreground shadow-md"
                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    }`}
            >
                {label}
            </Link>
        </motion.div>
    );

    const MobileNavGroup = ({ group }: { group: (typeof navGroups)[0] }) => {
        const isActive = isGroupActive(group);
        const isExpanded = openGroups[group.label];

        return (
            <Collapsible
                open={isExpanded}
                onOpenChange={() => toggleGroup(group.label)}
            >
                <CollapsibleTrigger asChild>
                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className={`w-full flex items-center justify-between px-4 py-3 rounded-xl text-base font-medium transition-all duration-200 ${isActive
                                ? "bg-primary text-primary-foreground shadow-md"
                                : "text-muted-foreground hover:bg-muted hover:text-foreground"
                            }`}
                    >
                        <span>{group.label}</span>
                        <ChevronDown
                            className={`h-4 w-4 transition-transform duration-200 ${isExpanded ? "rotate-180" : ""
                                }`}
                        />
                    </motion.button>
                </CollapsibleTrigger>
                <CollapsibleContent className="space-y-1 mt-1 ml-4">
                    {group.links.map((link) => (
                        <MobileNavLink
                            key={link.href}
                            href={link.href}
                            label={link.label}
                            isActive={activeLink === link.href}
                            onClick={() => {
                                setActiveLink(link.href);
                                setIsOpen(false);
                            }}
                        />
                    ))}
                </CollapsibleContent>
            </Collapsible>
        );
    };

    const UserMenuContent = () => {
        if (!isLoggedIn) {
            return (
                <div className="flex items-center space-x-3">
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                        <Button
                            variant="ghost"
                            className="text-muted-foreground hover:text-foreground hover:bg-muted transition-all duration-200"
                            onClick={() => navigate("/login")}
                        >
                            Sign In
                        </Button>
                    </motion.div>
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                        <Button
                            className="bg-primary text-primary-foreground shadow-md hover:bg-primary/90 hover:shadow-lg transition-all duration-200"
                            onClick={() => navigate("/signup")}
                        >
                            Sign Up
                        </Button>
                    </motion.div>
                </div>
            );
        }

        return (
            <DropdownMenu>
                <DropdownMenuTrigger asChild>
                    <Button
                        variant="ghost"
                        size="icon"
                        className="rounded-full relative group"
                    >
                        <motion.div
                            whileHover={{ scale: 1.1 }}
                            transition={{ type: "spring", stiffness: 400, damping: 17 }}
                        >
                            <Avatar className="h-9 w-9 ring-2 ring-offset-2 ring-primary transition-all duration-200">
                                <AvatarFallback className="bg-primary text-primary-foreground">
                                    {
                                        //@ts-ignore
                                        user?.charAt(0).toUpperCase()
                                    }
                                </AvatarFallback>
                            </Avatar>
                        </motion.div>
                        <span className="absolute top-0 right-0 h-2.5 w-2.5 bg-green-500 rounded-full ring-2 ring-background" />
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                    align="end"
                    className="w-56 overflow-hidden rounded-xl p-1 shadow-lg"
                >
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.2 }}
                    >
                        <div className="px-3 py-2">
                            <p className="text-sm font-medium">{user}</p>
                            <p className="text-xs text-muted-foreground mt-0.5">Active now</p>
                        </div>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                            onClick={() => navigate("/profile")}
                            className="cursor-pointer hover:bg-muted rounded-lg transition-colors duration-150 py-2"
                        >
                            <User className="mr-2 h-4 w-4 text-primary" />
                            <span>Profile</span>
                        </DropdownMenuItem>
                        <DropdownMenuItem
                            onClick={handleLogout}
                            className="cursor-pointer hover:bg-destructive/10 rounded-lg transition-colors duration-150 py-2"
                        >
                            <LogOut className="mr-2 h-4 w-4 text-destructive" />
                            <span>Log out</span>
                        </DropdownMenuItem>
                    </motion.div>
                </DropdownMenuContent>
            </DropdownMenu>
        );
    };

    return (
        <motion.header
            className={`w-full sticky top-0 z-50 transition-all duration-500 ${scrolled
                    ? "bg-background/80 backdrop-blur-xl shadow-lg border-b border-border/50"
                    : "bg-background/60 backdrop-blur-sm"
                }`}
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
        >
            <div className="max-w-7xl mx-auto">
                <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
                    <Link to="/" className="flex items-center gap-2">
                        <motion.div
                            whileHover={{ scale: 1.05, rotate: 5 }}
                            transition={{ type: "spring", stiffness: 400, damping: 10 }}
                            className="flex items-center gap-2"
                        >
                            <div className="relative">
                                <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center">
                                    <Sparkles className="h-5 w-5 text-primary-foreground" />
                                </div>
                                <div className="absolute -inset-1 rounded-xl bg-primary/20 blur-sm -z-10" />
                            </div>
                            <span className="text-xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                                CareerPath
                            </span>
                        </motion.div>
                    </Link>

                    <nav className="hidden md:flex items-center space-x-1">
                        <NavLink
                            href="/"
                            label="Home"
                            isActive={activeLink === "/"}
                            onClick={() => setActiveLink("/")}
                        />
                        <NavLink
                            href="/simulate"
                            label="Start Simulation"
                            isActive={activeLink === "/simulate"}
                            onClick={() => setActiveLink("/simulate")}
                        />
                        {navGroups.map((group) => (
                            <NavDropdown key={group.label} group={group} />
                        ))}
                    </nav>

                    <div className="flex items-center">
                        <UserMenuContent />

                        <Sheet open={isOpen} onOpenChange={setIsOpen}>
                            <SheetTrigger asChild>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="relative md:hidden ml-3"
                                >
                                    <Menu className="h-5 w-5" />
                                    <span className="sr-only">Open menu</span>
                                </Button>
                            </SheetTrigger>
                            <SheetContent
                                side="right"
                                className="p-0 bg-background border-l border-border w-[85vw] max-w-[320px]"
                            >
                                <div className="flex flex-col h-full">
                                    <motion.div
                                        className="p-4 border-b border-border flex items-center justify-between"
                                        initial={{ opacity: 0, y: -20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ duration: 0.3 }}
                                    >
                                        <div>
                                            <div className="flex items-center gap-2">
                                                <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center">
                                                    <Sparkles className="h-4 w-4 text-primary-foreground" />
                                                </div>
                                                <span className="text-lg font-bold">CareerPath</span>
                                            </div>
                                            <p className="mt-2 text-sm text-muted-foreground">
                                                AI-Powered Career Planning
                                            </p>
                                        </div>
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="rounded-full hover:bg-muted"
                                            onClick={() => setIsOpen(false)}
                                        >
                                            <X className="h-5 w-5" />
                                        </Button>
                                    </motion.div>

                                    <motion.div
                                        className="flex-1 p-4 overflow-y-auto"
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: 0.1, duration: 0.3 }}
                                    >
                                        <div className="space-y-2">
                                            <MobileNavLink
                                                href="/"
                                                label="Home"
                                                isActive={activeLink === "/"}
                                                onClick={() => {
                                                    setActiveLink("/");
                                                    setIsOpen(false);
                                                }}
                                            />
                                            <MobileNavLink
                                                href="/simulate"
                                                label="Start Simulation"
                                                isActive={activeLink === "/simulate"}
                                                onClick={() => {
                                                    setActiveLink("/simulate");
                                                    setIsOpen(false);
                                                }}
                                            />
                                            {navGroups.map((group) => (
                                                <MobileNavGroup key={group.label} group={group} />
                                            ))}
                                        </div>
                                    </motion.div>

                                    <motion.div
                                        className="p-4 border-t border-border"
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        transition={{ delay: 0.2 }}
                                    >
                                        {!isLoggedIn ? (
                                            <div className="grid grid-cols-2 gap-3">
                                                <Button
                                                    variant="outline"
                                                    className="w-full"
                                                    onClick={() => {
                                                        navigate("/login");
                                                        setIsOpen(false);
                                                    }}
                                                >
                                                    Sign In
                                                </Button>
                                                <Button
                                                    className="w-full bg-primary hover:bg-primary/90"
                                                    onClick={() => {
                                                        navigate("/signup");
                                                        setIsOpen(false);
                                                    }}
                                                >
                                                    Sign Up
                                                </Button>
                                            </div>
                                        ) : (
                                            <div>
                                                <div className="flex items-center mb-4">
                                                    <Avatar className="h-10 w-10 ring-2 ring-offset-2 ring-primary">
                                                        <AvatarFallback className="bg-primary text-primary-foreground">
                                                            {
                                                                //@ts-ignore
                                                                user?.charAt(0).toUpperCase()
                                                            }
                                                        </AvatarFallback>
                                                    </Avatar>
                                                    <div className="ml-3">
                                                        <p className="text-base font-medium">
                                                            {user}
                                                        </p>
                                                        <p className="text-xs text-muted-foreground">Active now</p>
                                                    </div>
                                                </div>
                                                <div className="grid grid-cols-2 gap-3">
                                                    <Button
                                                        variant="outline"
                                                        className="w-full justify-center"
                                                        onClick={() => {
                                                            navigate("/profile");
                                                            setIsOpen(false);
                                                        }}
                                                    >
                                                        Profile
                                                    </Button>
                                                    <Button
                                                        variant="destructive"
                                                        className="w-full justify-center"
                                                        onClick={() => {
                                                            handleLogout();
                                                            setIsOpen(false);
                                                        }}
                                                    >
                                                        Log out
                                                    </Button>
                                                </div>
                                            </div>
                                        )}
                                    </motion.div>
                                </div>
                            </SheetContent>
                        </Sheet>
                    </div>
                </div>
            </div>
        </motion.header>
    );
};

export default Navbar;