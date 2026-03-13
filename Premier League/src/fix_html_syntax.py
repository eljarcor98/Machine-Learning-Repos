import os

def fix_html_syntax():
    html_path = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\reports\match_viewer_everton_burnley.html"
    
    if not os.path.exists(html_path):
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # The error was: [ [ { ... } ] ]
    # We want: [ { ... } ]
    # Also fix the trailing closure
    
    bad_start = "const PASSES = [\n      ["
    good_start = "const PASSES = ["
    
    if bad_start in content:
        content = content.replace(bad_start, good_start)
        # Fix the matching end
        bad_end = "      ]\n    ];"
        good_end = "    ];"
        content = content.replace(bad_end, good_end)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("CSS/JS Syntax fixed successfully.")
    else:
        # Check if it was just slightly different
        if "const PASSES = [\n      [\n      {" in content:
            content = content.replace("const PASSES = [\n      [\n      {", "const PASSES = [\n      {")
            content = content.replace("      ]\n    ];", "    ];")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Syntax fixed (variant 2).")
        else:
            print("Could not find patterns to fix.")

if __name__ == "__main__":
    fix_html_syntax()
