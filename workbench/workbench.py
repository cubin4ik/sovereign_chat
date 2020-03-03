class SomeClass:
    value = 5


class SomeOtherClass(SomeClass):
    pass

instance = SomeClass()
another_instance = SomeOtherClass()

print(instance.value)
print(another_instance.value)
print("-" * 10)
another_instance.value = 75
print(instance.value)
print(another_instance.value)
