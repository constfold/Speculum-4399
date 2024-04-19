package unit4399.events
{
   import flash.events.Event;
   
   public class ShopEvent extends Event
   {
      
      public static const SHOP_GET_PACKAGEINFO:String = "getPacakgeInfo";
      
      public static const SHOP_DEL_SUCC:String = "delItemSuc";
      
      public static const SHOP_ERROR:String = "shopError";
      
      public static const SHOP_ADD_SUCC:String = "addItemSuc";
      
      public static const SHOP_ADDFREE_SUCC:String = "addFreeItemSuc";
      
      public static const SHOP_UPDATEPRO_SUCC:String = "updateProSuc";
      
      public static const SHOP_UPDATE_EXTEND:String = "updateExtend";
      
      public static const SHOP_GET_FREEPACKAGEINFO:String = "getFreePacakgeInfo";
      
      public static const SHOP_GET_PAYPACKAGEINFO:String = "getPayPacakgeInfo";
      
      public static const SHOP_GET_TYPENOTICE:String = "getTypeNotice";
      
      public static const SHOP_MODIFY_EX:String = "modifyEx";
      
      public static const SHOP_CLEARITEMS_EXTYPE:String = "clearItemsByExType";
      
      public static const SHOP_ERROR_ND:String = "shopErrorNd";
      
      public static const SHOP_BUY_ND:String = "shopBuyNd";
      
      public static const SHOP_GET_LIST:String = "shopGetList";
       
      
      protected var _data:Object;
      
      public function ShopEvent(type:String, dataOb:Object = null, bubbles:Boolean = false, cancelable:Boolean = false)
      {
         super(type,bubbles,cancelable);
         this._data = dataOb;
      }
      
      public function get data() : Object
      {
         return this._data;
      }
      
      override public function clone() : Event
      {
         return new ShopEvent(type,this.data,bubbles,cancelable);
      }
   }
}
