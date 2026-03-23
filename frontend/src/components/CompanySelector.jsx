// function CompanySelector({ companies, selected, onToggle }) {
//     return (
//         <div className="card">
//             <h2>🏢 Select Companies</h2>
//             <div className="company-grid">
//                 {companies.map((c) => (
//                     <button
//                         key={c.name}
//                         className={`company-chip ${selected.includes(c.name) ? "selected" : ""
//                             } ${!c.available ? "disabled" : ""}`}
//                         onClick={() => c.available && onToggle(c.name)}
//                         disabled={!c.available}
//                     >
//                         {c.name}
//                         {!c.available && <span className="badge">SOON</span>}
//                     </button>
//                 ))}
//             </div>
//         </div>
//     );
// }

// export default CompanySelector;

import { useState, useRef, useEffect } from "react";

function CompanySelector({ companies, selected, onToggle }) {
    const [open, setOpen] = useState(false);
    const [search, setSearch] = useState("");
    const wrapperRef = useRef(null);

    // Close dropdown when clicking outside
    useEffect(() => {
        function handleClickOutside(e) {
            if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
                setOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const filtered = companies.filter((c) =>
        c.name.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div className="card">
            <h2>🏢 Select Companies</h2>
            <div className="select-wrapper" ref={wrapperRef}>
                <div className="select-input" onClick={() => setOpen(!open)}>
                    {selected.length > 0 ? (
                        <div className="selected-tags">
                            {selected.map((name) => (
                                <span key={name} className="selected-tag">
                                    {name}
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onToggle(name);
                                        }}
                                    >
                                        ×
                                    </button>
                                </span>
                            ))}
                        </div>
                    ) : (
                        <span className="select-placeholder">Search or select companies...</span>
                    )}
                    <span className="select-arrow">{open ? "▲" : "▼"}</span>
                </div>

                {open && (
                    <div className="select-dropdown">
                        <input
                            className="select-search"
                            type="text"
                            placeholder="Type to search..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            autoFocus
                        />
                        <div className="select-options">
                            {filtered.map((c) => (
                                <div
                                    key={c.name}
                                    className={`select-option ${selected.includes(c.name) ? "selected" : ""
                                        } ${!c.available ? "disabled" : ""}`}
                                    onClick={() => {
                                        if (c.available) onToggle(c.name);
                                    }}
                                >
                                    <span>{c.name}</span>
                                    {!c.available && <span className="badge">SOON</span>}
                                    {selected.includes(c.name) && <span className="checkmark">✓</span>}
                                </div>
                            ))}
                            {filtered.length === 0 && (
                                <div className="select-option disabled">No companies found</div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default CompanySelector;
