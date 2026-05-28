def calculate_fibonacci(n):
    """Calculate fibonacci number at position n"""
    if n <= 1:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)


class DataProcessor:
    def __init__(self, data):
        self.data = data

    def process(self):
        """Process data and return results"""
        return [x * 2 for x in self.data]

    def filter_data(self, threshold):
        """Filter data by threshold"""
        return [x for x in self.data if x > threshold]


def merge_lists(list1, list2):
    """Merge two sorted lists"""
    result = []
    i = j = 0
    while i < len(list1) and j < len(list2):
        if list1[i] <= list2[j]:
            result.append(list1[i])
            i += 1
        else:
            result.append(list2[j])
            j += 1
    return result + list1[i:] + list2[j:]
