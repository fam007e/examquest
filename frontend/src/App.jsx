import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import {
    Search,
    Download,
    FileText,
    BookOpen,
    Filter,
    Loader2,
    ChevronRight,
    ExternalLink,
    Github,
    Star,
    Layers,
    Sparkles,
    ArrowLeft,
    Menu,
    X,
    GraduationCap,
    BookMarked
} from 'lucide-react';
// eslint-disable-next-line no-unused-vars
import { motion, AnimatePresence } from 'framer-motion';
import { getSubjectIcon } from './components/SubjectIcons';

const API_BASE = 'http://localhost:8000';

const SkeletonCard = () => (
    <div className="card animate-shimmer">
        <div className="flex justify-between items-start mb-4">
            <div className="w-14 h-14 bg-white/5 rounded-2xl" />
            <div className="w-8 h-8 bg-white/5 rounded-full" />
        </div>
        <div className="space-y-3">
            <div className="h-5 bg-white/5 rounded-lg w-3/4" />
            <div className="h-3 bg-white/5 rounded-lg w-1/2" />
        </div>
    </div>
);

function App() {
    const [boards, setBoards] = useState([]);
    const [selectedBoard, setSelectedBoard] = useState(null);
    const [levels, setLevels] = useState([]);
    const [selectedLevel, setSelectedLevel] = useState(null);
    const [subjects, setSubjects] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [selectedSubject, setSelectedSubject] = useState(null);
    const [papers, setPapers] = useState([]);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [favorites, setFavorites] = useState(() => {
        const saved = localStorage.getItem('exam_favorites');
        return saved ? JSON.parse(saved) : [];
    });

    useEffect(() => {
        fetchBoards();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    useEffect(() => {
        localStorage.setItem('exam_favorites', JSON.stringify(favorites));
    }, [favorites]);

    const fetchBoards = async () => {
        try {
            const res = await axios.get(`${API_BASE}/boards`);
            setBoards(res.data);
            if (res.data.length > 0) {
                handleBoardSelect(res.data[0]);
            }
        } catch (err) {
            console.error("Failed to fetch boards", err);
        }
    };

    const handleBoardSelect = async (board) => {
        setSelectedBoard(board);
        setSelectedSubject(null);
        setPapers([]);
        setLoading(true);
        setMobileMenuOpen(false);
        try {
            const res = await axios.get(`${API_BASE}/levels/${board.id}`);
            setLevels(res.data);
            setSelectedLevel(res.data[0]);
            fetchSubjects(board, res.data[0]);
        } catch {
            setLoading(false);
        }
    };

    const fetchSubjects = async (board, level) => {
        setLoading(true);
        setSubjects([]);
        setSelectedSubject(null);
        try {
            const res = await axios.get(`${API_BASE}/subjects`, {
                params: { source: board.source, board: board.board, level: level }
            });
            setSubjects(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const fetchPapers = async (subject, boardOverride = null) => {
        setSelectedSubject(subject);
        setLoading(true);
        try {
            const board = boardOverride || selectedBoard;
            const res = await axios.get(`${API_BASE}/papers`, {
                params: {
                    subject_url: subject.url,
                    board: board.board,
                    source: board.source
                }
            });
            setPapers(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const toggleFavorite = (e, subject) => {
        e.stopPropagation();
        const isFav = favorites.some(f => f.url === subject.url);
        if (isFav) {
            setFavorites(favorites.filter(f => f.url !== subject.url));
        } else {
            setFavorites([...favorites, { ...subject, board: selectedBoard, level: selectedLevel }]);
        }
    };

    const downloadPaper = (paper) => {
        const url = `${API_BASE}/download?url=${encodeURIComponent(paper.url)}&filename=${encodeURIComponent(paper.name)}`;
        window.location.href = url;
    };

    const downloadMerged = async () => {
        if (papers.length === 0) return;
        setLoading(true);
        try {
            const res = await axios.post(`${API_BASE}/merge`, {
                papers: papers.slice(0, 10),
                output_name: `${selectedSubject.name}_merged.pdf`
            }, { responseType: 'blob' });

            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `${selectedSubject.name}_merged.pdf`);
            document.body.appendChild(link);
            link.click();
        } catch (err) {
            console.error("Failed to merge", err);
        } finally {
            setLoading(false);
        }
    };

    const filteredSubjects = subjects.filter(s =>
        s.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const mergedPapers = useMemo(() => {
        const groups = {};
        papers.forEach(p => {
            if (!groups[p.type]) groups[p.type] = [];
            groups[p.type].push(p);
        });
        return groups;
    }, [papers]);

    const getSubjectCategory = (name) => {
        const n = name.toLowerCase();
        if (n.includes('physics') || n.includes('chem') || n.includes('biol')) return 'science';
        if (n.includes('math') || n.includes('calculus')) return 'math';
        if (n.includes('english') || n.includes('french') || n.includes('language')) return 'languages';
        if (n.includes('history') || n.includes('geograph') || n.includes('econom')) return 'humanities';
        if (n.includes('art') || n.includes('music') || n.includes('design')) return 'arts';
        return 'default';
    };

    return (
        <div className="flex bg-dark-bg min-h-screen text-gray-200">

            {/* Mobile Menu Overlay */}
            <AnimatePresence>
                {mobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
                        onClick={() => setMobileMenuOpen(false)}
                    />
                )}
            </AnimatePresence>

            {/* Sidebar */}
            <aside className={`
        w-80 flex-col border-r border-dark-border glass fixed lg:sticky top-0 h-screen overflow-y-auto z-50
        transition-transform duration-300 ease-out
        ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        lg:flex
      `}>
                {/* Close button for mobile */}
                <button
                    onClick={() => setMobileMenuOpen(false)}
                    className="absolute top-4 right-4 p-2 rounded-xl bg-white/5 hover:bg-white/10 transition-colors lg:hidden"
                >
                    <X size={20} />
                </button>

                <div className="p-8 border-b border-white/5 space-y-8">
                    {/* Logo */}
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-2xl flex items-center justify-center shadow-glow">
                            <GraduationCap className="text-white" size={24} />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold gradient-text">ExamQuest</h1>
                            <p className="text-xs text-gray-500 mt-0.5">Past Papers Hub</p>
                        </div>
                    </div>

                    {/* Boards Selection */}
                    <div className="space-y-3">
                        <p className="text-[10px] uppercase tracking-[0.2em] text-gray-500 font-bold ml-1">
                            Examination Boards
                        </p>
                        <div className="space-y-2">
                            {boards.map(board => (
                                <button
                                    key={board.id}
                                    onClick={() => handleBoardSelect(board)}
                                    className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all duration-300 text-sm font-medium group ${selectedBoard?.id === board.id
                                        ? 'bg-gradient-to-r from-primary to-secondary text-white shadow-lg shadow-primary/30'
                                        : 'hover:bg-white/5 text-gray-400 hover:text-gray-200 border border-transparent hover:border-white/10'
                                        }`}
                                >
                                    <Layers size={18} className={selectedBoard?.id === board.id ? '' : 'opacity-60'} />
                                    <div className="flex flex-col items-start min-w-0">
                                        <span className="truncate w-full">{board.board}</span>
                                        <span className={`text-[9px] px-1.5 py-0.5 rounded-md mt-0.5 uppercase tracking-wider font-bold ${selectedBoard?.id === board.id
                                            ? 'bg-white/20 text-white'
                                            : 'bg-white/5 text-gray-500 group-hover:text-gray-400 border border-white/5'
                                            }`}>
                                            {board.source}
                                        </span>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="flex-1 p-8 space-y-8">
                    {/* Bookmarks */}
                    {favorites.length > 0 && (
                        <div className="space-y-4">
                            <div className="flex items-center gap-2">
                                <BookMarked size={14} className="text-accent-amber" />
                                <p className="text-[10px] uppercase tracking-[0.2em] text-gray-500 font-bold">
                                    Bookmarks ({favorites.length})
                                </p>
                            </div>
                            <div className="space-y-2 max-h-48 overflow-y-auto custom-scrollbar">
                                {favorites.map(fav => (
                                    <button
                                        key={fav.url}
                                        onClick={async () => {
                                            setSelectedBoard(fav.board);
                                            setSelectedLevel(fav.level);
                                            setMobileMenuOpen(false);
                                            // Fetch papers immediately
                                            fetchPapers(fav, fav.board);

                                            // Also fetch the correct levels/subjects for this board update the sidebar/header
                                            try {
                                                const res = await axios.get(`${API_BASE}/levels/${fav.board.id}`);
                                                setLevels(res.data);
                                            } catch (err) {
                                                console.error("Failed to sync levels on bookmark click", err);
                                            }
                                        }}
                                        className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl bg-white/5 border border-white/5 hover:border-accent-amber/30 hover:bg-accent-amber/5 transition-all text-xs text-left group"
                                    >
                                        <div className="w-7 h-7 bg-accent-amber/10 rounded-lg flex items-center justify-center group-hover:bg-accent-amber/20 text-accent-amber shrink-0">
                                            <Star size={12} fill="currentColor" />
                                        </div>
                                        <span className="truncate flex-1 text-gray-300 group-hover:text-white">{fav.name}</span>
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Quick Stats */}
                    <div className="glass rounded-xl p-4 space-y-3">
                        <p className="text-[10px] uppercase tracking-[0.2em] text-gray-500 font-bold">Quick Stats</p>
                        <div className="grid grid-cols-2 gap-3">
                            <div className="text-center p-3 bg-white/5 rounded-lg">
                                <p className="text-lg font-bold text-primary">{subjects.length}</p>
                                <p className="text-[10px] text-gray-500">Subjects</p>
                            </div>
                            <div className="text-center p-3 bg-white/5 rounded-lg">
                                <p className="text-lg font-bold text-accent-emerald">{favorites.length}</p>
                                <p className="text-[10px] text-gray-500">Saved</p>
                            </div>
                        </div>
                    </div>

                    {/* Credits */}
                    <div className="space-y-3">
                        <p className="text-[10px] uppercase tracking-[0.2em] text-gray-500 font-bold ml-1">About</p>
                        <a
                            href="https://github.com/fam007e/OandALvl-exam-paper-downloader/tree/main"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-3 px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 hover:border-white/10 transition-all text-xs group"
                        >
                            <Github size={18} className="text-gray-400 group-hover:text-white transition-colors" />
                            <span className="text-gray-400 group-hover:text-white transition-colors">View on GitHub</span>
                        </a>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col h-screen overflow-hidden">

                {/* Top Header */}
                <header className="px-6 lg:px-10 py-5 border-b border-dark-border flex items-center justify-between gap-4 lg:gap-8 glass sticky top-0 z-10">
                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setMobileMenuOpen(true)}
                        className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-all lg:hidden"
                    >
                        <Menu size={20} />
                    </button>

                    {/* Search Bar */}
                    <div className="relative flex-1 max-w-2xl">
                        <input
                            type="text"
                            placeholder="Search subjects, codes, or topics..."
                            className="input pl-6 pr-12 py-3.5 rounded-2xl glow-focus"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                        <Search className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500" size={20} />
                    </div>

                    {/* Level Pills */}
                    <div className="hidden sm:flex items-center gap-2">
                        {levels.map(level => (
                            <button
                                key={level}
                                onClick={() => {
                                    setSelectedLevel(level);
                                    setSelectedSubject(null);
                                    setPapers([]);
                                    fetchSubjects(selectedBoard, level);
                                }}
                                className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all duration-300 whitespace-nowrap ${selectedLevel === level
                                    ? 'bg-primary/20 text-primary border border-primary/30 shadow-glow-sm'
                                    : 'bg-dark-card border border-dark-border text-gray-500 hover:border-white/20 hover:text-gray-300'
                                    }`}
                            >
                                {level}
                            </button>
                        ))}
                    </div>
                </header>

                {/* Mobile Level Selector */}
                <div className="flex sm:hidden gap-2 px-4 py-3 overflow-x-auto border-b border-dark-border bg-dark-bg/80">
                    {levels.map(level => (
                        <button
                            key={level}
                            onClick={() => {
                                setSelectedLevel(level);
                                setSelectedSubject(null);
                                setPapers([]);
                                fetchSubjects(selectedBoard, level);
                            }}
                            className={`px-4 py-2 rounded-lg text-xs font-bold shrink-0 transition-all ${selectedLevel === level
                                ? 'bg-primary text-white'
                                : 'bg-white/5 text-gray-500'
                                }`}
                        >
                            {level}
                        </button>
                    ))}
                </div>

                {/* Scrollable Content Area */}
                <div className="flex-1 overflow-y-auto p-6 lg:p-10 custom-scrollbar">
                    <AnimatePresence mode="wait">
                        {!selectedSubject ? (
                            <motion.div
                                key="grid"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                className="space-y-6"
                            >
                                {/* Section Header */}
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h2 className="text-2xl font-bold">
                                            {selectedBoard?.name || 'Subjects'}
                                        </h2>
                                        <p className="text-gray-500 text-sm mt-1">
                                            {filteredSubjects.length} subjects available • {selectedLevel}
                                        </p>
                                    </div>
                                </div>

                                {/* Subject Grid */}
                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
                                    {loading ? (
                                        Array.from({ length: 8 }).map((_, i) => <SkeletonCard key={i} />)
                                    ) : filteredSubjects.length > 0 ? (
                                        filteredSubjects.map((subject, idx) => {
                                            const isFav = favorites.some(f => f.url === subject.url);
                                            const category = getSubjectCategory(subject.name);
                                            return (
                                                <motion.div
                                                    layout
                                                    initial={{ opacity: 0, scale: 0.9 }}
                                                    animate={{ opacity: 1, scale: 1 }}
                                                    transition={{ delay: idx * 0.02 }}
                                                    key={subject.name}
                                                    onClick={() => fetchPapers(subject)}
                                                    className={`card-interactive relative group min-h-[180px] flex flex-col justify-between subject-${category}`}
                                                >
                                                    {/* Favorite Button */}
                                                    <button
                                                        onClick={(e) => toggleFavorite(e, subject)}
                                                        className={`absolute top-4 right-4 p-2.5 rounded-xl transition-all z-10 ${isFav
                                                            ? 'text-accent-amber bg-accent-amber/10 hover:bg-accent-amber/20'
                                                            : 'text-gray-600 bg-white/5 opacity-0 group-hover:opacity-100 hover:text-accent-amber hover:bg-accent-amber/10'
                                                            }`}
                                                    >
                                                        <Star size={16} fill={isFav ? "currentColor" : "none"} />
                                                    </button>

                                                    <div className="space-y-4">
                                                        {/* Subject Icon */}
                                                        <div className="w-14 h-14 bg-gradient-to-br from-primary/20 to-secondary/10 rounded-2xl flex items-center justify-center text-primary group-hover:scale-110 transition-transform duration-300">
                                                            {getSubjectIcon(subject.name, "w-7 h-7")}
                                                        </div>

                                                        {/* Subject Info */}
                                                        <div className="space-y-1.5">
                                                            <h3 className="font-bold text-base leading-snug group-hover:text-primary transition-colors line-clamp-2">
                                                                {subject.name}
                                                            </h3>
                                                            <div className="flex items-center gap-2 text-[10px] text-gray-500 font-semibold uppercase tracking-wider">
                                                                <span>{selectedBoard?.board}</span>
                                                                <span className="w-1 h-1 bg-gray-600 rounded-full" />
                                                                <span>{selectedLevel}</span>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    {/* Footer with paper types */}
                                                    <div className="mt-5 flex items-center justify-between">
                                                        <div className="flex gap-1.5">
                                                            <span className="px-2 py-1 text-[10px] font-bold rounded-md paper-qp">QP</span>
                                                            <span className="px-2 py-1 text-[10px] font-bold rounded-md paper-ms">MS</span>
                                                        </div>
                                                        <ChevronRight
                                                            size={18}
                                                            className="text-primary opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all"
                                                        />
                                                    </div>
                                                </motion.div>
                                            );
                                        })
                                    ) : (
                                        <div className="col-span-full flex flex-col items-center justify-center py-32 space-y-4">
                                            <div className="w-24 h-24 bg-white/5 rounded-full flex items-center justify-center">
                                                <Search size={40} className="text-gray-700" />
                                            </div>
                                            <div className="text-center space-y-2">
                                                <p className="text-gray-400 font-medium text-lg">No subjects found</p>
                                                <p className="text-gray-600 text-sm">Try adjusting your search or selecting a different level</p>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="papers"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className="space-y-8"
                            >
                                {/* Papers Header */}
                                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5">
                                    <div className="flex items-center gap-5">
                                        <button
                                            onClick={() => setSelectedSubject(null)}
                                            className="w-12 h-12 flex items-center justify-center glass rounded-xl hover:bg-white/10 transition-all shrink-0"
                                        >
                                            <ArrowLeft size={22} />
                                        </button>
                                        <div>
                                            <h2 className="text-2xl lg:text-3xl font-extrabold">{selectedSubject.name}</h2>
                                            <p className="text-gray-500 mt-1">{selectedBoard?.name} • {selectedLevel}</p>
                                        </div>
                                    </div>

                                    <button
                                        onClick={downloadMerged}
                                        disabled={loading || papers.length === 0}
                                        className="btn-primary py-3.5 px-6 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        <Download size={18} />
                                        <span>Download All Merged</span>
                                    </button>
                                </div>

                                {loading ? (
                                    <div className="py-24 flex flex-col items-center gap-4">
                                        <Loader2 className="animate-spin text-primary" size={48} />
                                        <p className="text-gray-500 font-medium animate-pulse">Loading exam papers...</p>
                                    </div>
                                ) : (
                                    <div className="space-y-10">
                                        {Object.entries(mergedPapers).map(([type, list]) => (
                                            <section key={type} className="space-y-5">
                                                {/* Section Header */}
                                                <div className="flex items-center gap-4">
                                                    <div className={`w-1.5 h-8 rounded-full ${type === 'qp' ? 'bg-accent-blue' :
                                                        type === 'ms' ? 'bg-accent-emerald' : 'bg-gray-500'
                                                        }`} />
                                                    <h4 className="text-sm font-bold uppercase tracking-[0.25em] text-gray-400">
                                                        {type === 'qp' ? 'Question Papers' : type === 'ms' ? 'Mark Schemes' : 'Other Resources'}
                                                    </h4>
                                                    <span className="px-2.5 py-1 text-xs font-bold rounded-full bg-white/5 text-gray-500">
                                                        {list.length}
                                                    </span>
                                                    <div className="flex-1 border-b border-white/5" />
                                                </div>

                                                {/* Papers Grid */}
                                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                                                    {list.map((paper, idx) => (
                                                        <motion.div
                                                            initial={{ opacity: 0, y: 10 }}
                                                            animate={{ opacity: 1, y: 0 }}
                                                            transition={{ delay: idx * 0.02 }}
                                                            key={paper.url}
                                                            className="glass rounded-xl p-4 flex items-center justify-between group hover:border-primary/30 transition-all"
                                                        >
                                                            <div className="flex items-center gap-4 min-w-0">
                                                                <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${type === 'qp' ? 'bg-accent-blue/10 text-accent-blue' :
                                                                    type === 'ms' ? 'bg-accent-emerald/10 text-accent-emerald' :
                                                                        'bg-gray-500/10 text-gray-400'
                                                                    }`}>
                                                                    <FileText size={18} />
                                                                </div>
                                                                <p className="text-sm font-semibold truncate group-hover:text-primary transition-colors">
                                                                    {paper.name}
                                                                </p>
                                                            </div>
                                                            <div className="flex items-center gap-1 shrink-0">
                                                                <a
                                                                    href={paper.url}
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    className="p-2.5 text-gray-500 hover:text-white hover:bg-white/5 rounded-lg transition-all"
                                                                    title="Preview Online"
                                                                >
                                                                    <ExternalLink size={16} />
                                                                </a>
                                                                <button
                                                                    onClick={() => downloadPaper(paper)}
                                                                    className="p-2.5 text-primary hover:bg-primary/10 rounded-lg transition-all"
                                                                    title="Download"
                                                                >
                                                                    <Download size={16} />
                                                                </button>
                                                            </div>
                                                        </motion.div>
                                                    ))}
                                                </div>
                                            </section>
                                        ))}
                                    </div>
                                )}
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </main>
        </div>
    );
}

export default App;
