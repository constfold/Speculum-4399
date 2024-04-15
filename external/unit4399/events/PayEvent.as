package unit4399.events
{
   import flash.events.Event;
   
   public class PayEvent extends Event
   {
      
      public static const LOG:String = "logsuccess";
      
      public static const INC_MONEY:String = "incMoney";
      
      public static const DEC_MONEY:String = "decMoney";
      
      public static const GET_MONEY:String = "getMoney";
      
      public static const PAY_MONEY:String = "payMoney";
      
      public static const PAY_ERROR:String = "payError";
       
      
      protected var _data:Object;
      
      public function PayEvent(param1:String, param2:Object, param3:Boolean = false, param4:Boolean = false)
      {
         super(param1,param3,param4);
         this._data = param2;
      }
      
      public function get data() : Object
      {
         return this._data;
      }
      
      override public function clone() : Event
      {
         return new PayEvent(type,this.data,bubbles,cancelable);
      }
   }
}
