import os

out_dir = os.path.join(os.path.dirname(__file__), 'static', 'images', 'circuits')
os.makedirs(out_dir, exist_ok=True)

# Neon-styled SVG paths representing stylized F1 circuits
circuits = {
    "bahrain.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100%" height="100%">
    <defs>
        <filter id="neon" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur1" />
            <feGaussianBlur in="SourceGraphic" stdDeviation="5" result="blur2" />
            <feMerge>
                <feMergeNode in="blur2" />
                <feMergeNode in="blur1" />
                <feMergeNode in="SourceGraphic" />
            </feMerge>
        </filter>
    </defs>
    <path d="M 20 80 L 20 40 Q 20 20 40 20 L 70 20 Q 90 20 90 40 L 90 60 Q 90 80 70 80 Z" 
          fill="none" stroke="#E10600" stroke-width="3" filter="url(#neon)"/>
    <circle cx="20" cy="60" r="3" fill="#FFF"/>
</svg>''',
    
    "saudi.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100%" height="100%">
    <defs>
        <filter id="neon" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur1" />
            <feGaussianBlur in="SourceGraphic" stdDeviation="5" result="blur2" />
            <feMerge><feMergeNode in="blur2" /><feMergeNode in="blur1" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
    </defs>
    <path d="M 10 90 L 30 10 L 50 30 L 70 10 L 90 90 Z" 
          fill="none" stroke="#00D26A" stroke-width="3" filter="url(#neon)"/>
    <circle cx="30" cy="50" r="3" fill="#FFF"/>
</svg>''',

    "australia.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100%" height="100%">
    <defs>
        <filter id="neon" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur1" />
            <feGaussianBlur in="SourceGraphic" stdDeviation="5" result="blur2" />
            <feMerge><feMergeNode in="blur2" /><feMergeNode in="blur1" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
    </defs>
    <path d="M 50 10 Q 90 10 90 50 Q 90 90 50 90 Q 10 90 10 50 Q 10 10 50 10 Z" 
          fill="none" stroke="#FCD116" stroke-width="3" filter="url(#neon)"/>
    <circle cx="50" cy="10" r="3" fill="#FFF"/>
</svg>'''
}

for filename, content in circuits.items():
    with open(os.path.join(out_dir, filename), 'w') as f:
        f.write(content)

print(f"Generated {len(circuits)} circuit SVGs in {out_dir}")
