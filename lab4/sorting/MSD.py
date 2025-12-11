class MSDRadixSorter:
    """Класс для MSD сортировки."""

    @staticmethod
    def sort(arr, key=str, d=0):
        arr = list(arr)
        if len(arr) <= 1:
            return arr

        R = 257
        buckets = [[] for _ in range(R)]

        for x in arr:
            s = key(x)
            c = ord(s[d]) if d < len(s) else -1
            buckets[c + 1].append(x)

        result = []
        for bucket in buckets:
            if len(bucket) > 1:
                result.extend(MSDRadixSorter.sort(bucket, key, d + 1))
            else:
                result.extend(bucket)

        return result


# Старый интерфейс сохранён
def msd_radix_sort(arr, key=str, d=0):
    return MSDRadixSorter.sort(arr, key, d)
