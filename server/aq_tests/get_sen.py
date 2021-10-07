from test_functions import get_aq_sen, post_aq

print("Posting 5 samples...")
post_aq(5)
print("Done.")

print("Requesting last 5 samples of temp...")
print(get_aq_sen('temp', 5))
