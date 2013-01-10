<?php

class SDO_Mock
{
    public $requestCount = 0;
    public $returnJunk = false;
    
    public function get($query,$args,$type=MYSQL_BOTH,$col_id=null) {
        $this->requestCount += 1;
        
        if($this->returnJunk) {
            return array(true);
        } else {
            return array();
        }
    }
    
    public function resetCount() {
        $this->requestCount = 0;
    }
}