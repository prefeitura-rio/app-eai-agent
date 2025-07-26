export function exportToCsv(filename: string, rows: object[]) {
    if (!rows || rows.length === 0) {
        return;
    }

    const separator = ',';
    const keys = Object.keys(rows[0]);
    const csvContent =
        keys.join(separator) +
        '\n' +
        rows.map(row => {
            return keys.map(k => {
                let cell = row[k as keyof typeof row] === null || row[k as keyof typeof row] === undefined ? '' : row[k as keyof typeof row];
                cell = cell instanceof Date
                    ? cell.toLocaleString()
                    : typeof cell === 'object' ? JSON.stringify(cell).replace(/"/g, '""') : String(cell).replace(/"/g, '""');
                return `"${cell}"`;
            }).join(separator);
        }).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}
