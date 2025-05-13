def query(x):
    return -1 * (x - 7)**2 + 49
    
def find_peak(N: int) -> int:
    current = N // 2  
    while True:
        current_val = query(current)
        
        
        left_val = query(current - 1) if current > 0 else float('-inf')
        right_val = query(current + 1) if current < N else float('-inf')
        
        if current_val >= left_val and current_val >= right_val:
            return current
        
        elif left_val > current_val:
            current -= 1
        else:  
            current += 1

if __name__ == "__main__":
    N = 20  
    peak = find_peak(N)
    print(f"PEAK: {peak} | ELEVATION: {query(peak)}")