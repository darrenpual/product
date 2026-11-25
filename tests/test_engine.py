from engine import rank

def test_rank():
    cfg=dict(design=.4,price=.3,innovation=.15,marketing=.1,market_response=.05,min_total=80,min_design=75,min_price=60,category_limit=15,daily_limit=100,grade_s=90,grade_a=85,grade_b=70,grade_c=55)
    item=dict(product_id="fixture",category_id="BEAUTY_DEVICE",sku_verified=True,price_cny=39,image_url="https://example.com/image",product_url="https://example.com/product",scores={k:90 for k in ("design","price","innovation","marketing","market_response")})
    assert rank([item,item],cfg)[0]["grade"]=="S"
    assert len(rank([item,item],cfg))==1
    assert rank([dict(item,sku_verified=False)],cfg)==[]
    assert rank([item],cfg,["fixture"])==[]
