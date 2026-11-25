from analysis_engine import price_score, analyze

def test_price():
    assert price_score(10,[20,30]) is None
    assert price_score(10,[20,30,40,50,60])["score"] == 100
    assert price_score(30,[30]*5)["score"] == 50

def test_missing_evidence():
    x={"product_id":"a","sku_verified":True,"price_cny":10}
    assert analyze([x],None)[0]["scores"] == {}
