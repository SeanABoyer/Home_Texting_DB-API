

var app = angular.module('HomeTextingApp', ['luegg.directives','base64']);
app.controller('HomeTextingController', function($scope, $http, $timeout,$base64,$location,$filter) {
	/*	Initilize Variables	*/
	$scope.validLogin = false;
	$scope.UserObj = {
			"username":"",
			"password":"",
			"phoneNumber":"",
			//"serverIP":$location.host(),
			"serverIP":"192.168.1.2",
			"updateAuth": function(){
				var auth = $base64.encode($scope.UserObj.username+":"+$scope.UserObj.password);
				$scope.UserObj.basicAuth = {"Authorization":"Basic "+auth};
					},
			"basicAuth":null
	}
	$scope.LoginRunning = false;
	toastr.options.newestOnTop = true;
	$scope.conversations = [];
	$scope.messageTextBox = "";
	/*	End Initilize Variables	*/
	
	/*	Define Classes*/
	class Conversation{
		constructor(number){
			var c = this;
			this.unreadCount = 0;
			this.number = number;
			this.name = number;
			this.lastMessageTime = "3:00PM";
			this.messages = [];
			this.lastMessage = null;
			this.AddMessage = function(message) {
				if(this != $scope.activeConversation){
					this.unreadCount+=1;
				}
				this.messages.push(message);
				this.lastMessage = message;
				this.lastMessageTime = message.time;
			}
			$http.get("http://"+$scope.UserObj.serverIP+"/message/by/ID/"+number+"/0/",{"headers":$scope.UserObj.basicAuth}).then(function(result){
				for(var j = 0; result.data.length > j; j++){
					c.AddMessage(new Message(result.data[j].ID,result.data[j].MESSAGE,result.data[j].TO,result.data[j].FROM,result.data[j].TIME))
				}
				c.unreadCount = 0;
			}, function(result){
				toastr.error("Error adding messages to "+c.number);
			});	
		}
	}
	class Message{
		constructor(id,message, To, From, time){
			this.numberTO = To;
			this.numberFrom = From;
			this.message = message;
//			this.time = time;
			this.id = id;
			this.time = "2:00PM";
		}
	}
	/*	End Define Classes */
	
	function getConversations(){
		$http.get("http://"+$scope.UserObj.serverIP+"/conversation/"+$scope.UserObj.phoneNumber+"/",{"headers":$scope.UserObj.basicAuth}).then(function(result){
			for(var i = 0; result.data.length > i; i++){
				$scope.conversations.push(new Conversation(result.data[i].CONVERSATIONNUMBER));
			}
			$scope.activeConversation = $scope.conversations[0];
		}, function(result){
			toastr.error("Initilazing Conversations");
		});
	}
	$scope.conversationClicked = function(conversation) {
		//Find All active Convs and Make them inactive
		for(var i = 0; $scope.conversations.length > i; i++){
			$scope.conversations[i].active = false;
		}
		//Find the conv that was clicked and make it active
		$scope.activeConversation = $scope.conversations[$scope.conversations.indexOf(conversation)];
		$scope.activeConversation.active = true;
		conversation.unreadCount = 0;
	}
	/*	Login	*/
	$scope.Login = function(){
		if($scope.LoginRunning){
			return;
		}
		if ($scope.UserObj.username == "" || $scope.UserObj.password == ""){
			toastr.error("Please supply a username and password.");
			return;
		}
		$scope.LoginRunning = true;
		toastr["info"]("Testing Server IP.");
		$http.get("http://"+$scope.UserObj.serverIP+"/validateIP/",{timeout:2000}).then(function(result){
			toastr.remove();
			toastr.success("Valid Server IP.");
			toastr["info"]("Validating Credentials.");
			$http.get("http://"+$scope.UserObj.serverIP+"/validateLogin/",{"headers":$scope.UserObj.basicAuth}).then(function(result){
				toastr.remove();
				toastr.success("Credentials Valid. Access Granted.");
				$scope.UserObj.phoneNumber = result.data.phoneNumber;
				$scope.validLogin = true;
				getConversations();
				$scope.LoginRunning = false;
				connectToMQTT();
			},function(result){
				toastr.error("Credentials Invalid. Access Denied.");
				$scope.LoginRunning = false;
			});
		},function(result){
			toastr.remove();
			toastr.error("Invalid Server IP.");
			$scope.LoginRunning = false;
		});
	}
	$scope.LoginbyKey = function (event){
		if(event.keyCode == 13){
			$scope.Login();
		}
	}	
	/*	Sending Messages	*/
	$scope.submit = function(event){
		if(event.keyCode == 13){
			$scope.sendMessage($scope.activeConversation);
		}
	}
	$scope.sendMessage = function(conversation){
		if ($scope.messageTextBox == "" || $scope.messageTextBox == null){
			return
		}
		var data = {"CONVERSATIONNUMBER":conversation.number,
					"FROM":$scope.UserObj.phoneNumber,
					"TO":conversation.number,
					"MESSAGE":$scope.messageTextBox,
					"CLIENT":"AngularClient-"+$scope.UserObj.username
					}
		
		$http.post("http://"+$scope.UserObj.serverIP+"/message/by/PhoneNumber/",data,{"headers":$scope.UserObj.basicAuth}).then(function(result){
			conversation.AddMessage(new Message(result.data.ID,result.data.MESSAGE, result.data.TO, result.data.FROM, result.data.TIME));
		}, function(result){
			toastr.error("Message failed to deliver to server.");
		});	
		$scope.messageTextBox = "";
	}
	/* Dynamic Classes	*/
	$scope.getPersonClass = function (conversation){
		var classes = {"person":true, "activeConv":false}
		if ($scope.conversations.indexOf($scope.activeConversation) == $scope.conversations.indexOf(conversation)) {
			classes.activeConv = true;
		}
		return classes;
	}
	$scope.getMessageClass = function (message){
		var classes = {"bubble":true, "you":false, "me":false}
		if(message.numberTO == $scope.activeConversation.number){
			classes.me = true;
		} else {
			classes.you = true;
		}
		return classes;
	}	
	/*	[MQTT]Recieving Messages	*/
	function connectToMQTT(){
		client = new Paho.MQTT.Client($scope.UserObj.serverIP,Number(1884),"AngularClient-"+$scope.UserObj.username);
		client.onConnectionLost = onConnectionLost;
		client.onMessageArrived = onMessageArrived;
		client.connect({onSuccess:onConnect,onFailure:onFail});
	}
	function onConnectionLost(responseObject) {
		toastr.error("Lost connection to message server.");
	    console.log("onConnectionLost:"+responseObject);
	}
	function onMessageArrived(message) {
		var JsonMessage = JSON.parse(message.payloadString);
		if(JsonMessage.CLIENT != "AngularClient-"+$scope.UserObj.username){
			$http.get("http://"+$scope.UserObj.serverIP+"/message/by/ID/"+JsonMessage.CONVERSATIONNUMBER+"/"+(Number(JsonMessage.MESSAGEID))+"/",{"headers":$scope.UserObj.basicAuth}).then(function(result){
				//TODO:: What if a conversation does not exist?
				var conversation = $filter('filter')($scope.conversations, {"number":JsonMessage.CONVERSATIONNUMBER})[0];
				var messageOBJ = result.data[0];
				var newMessage = new Message(messageOBJ.ID,messageOBJ.MESSAGE,messageOBJ.TO,messageOBJ.FROM,messageOBJ.TIME)
				if(conversation){
					conversation.AddMessage(newMessage);
				} else {
					var newConversation = new Conversation(messageOBJ.FROM);
					newConversation.AddMessage(newMessage);
					$scope.conversations.push(newConversation);
				}
			}, function(result){
				toastr.error("Updating Messages to "+c.number);
			});	
		}
	}
	function onConnect() {
		toastr.success("Connected to message server.");
		client.subscribe($scope.UserObj.username);
	}
	function onFail(){
		toast.error("Failed to connect to message server.");
	}
});


