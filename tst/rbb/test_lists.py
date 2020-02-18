from rbb.lists import Blacklist

def test_blacklist():
    assert "diablo" not in Blacklist()
    assert "diablo" in Blacklist("DIABLO")
    assert "DiAbLo" in Blacklist("diablo")
    some_blacklist = Blacklist()
    assert "foo" not in some_blacklist
    some_blacklist.add("FOO")
    assert "foo" in some_blacklist
    assert Blacklist() == Blacklist()
    assert Blacklist("Foo") == Blacklist("foo")
    assert Blacklist("diablo", "foo") == Blacklist("diAblo") + Blacklist("FOO")
    assert "FOO" in (Blacklist("bar", "foo") + Blacklist("diablo"))
    
