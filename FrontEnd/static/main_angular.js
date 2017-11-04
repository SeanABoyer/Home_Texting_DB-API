

var app = angular.module('HomeTextingApp', ['luegg.directives']);
app.controller('HomeTextingController', function($scope, $http) {

	var Auth = {"Authorization":"Basic U2VhbjpwYXNz"};
	$scope.conversations = [];
	$http.get("http://localhost/conversation/18307652286/",{"headers":Auth}).then(function(result){
		for(var i = 0; result.data.length > i; i++){
			$scope.conversations.push(new Conversation(result.data[i].CONVERSATIONNUMBER));
		}
	}, function(result){
		console.log("ERROR");
	});
	$scope.activeConversation = $scope.conversations[0];

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
	
	
	setInterval(function(){
		
		$http.get("http://localhost/conversation/18307652286/",{"headers":Auth}).then(function(result){
			var convArray = [];
			for(var i = 0; result.data.length > i; i++){
				convArray.push(result.data[i].CONVERSATIONNUMBER);
			}
			for(var i = 0; $scope.conversations.length > i; i++){
				//Check if convArray contains the conversation. if yes. Remove it from the list. If not. do nothing.
				if(convArray.includes($scope.conversations[i].number)){
					//If Conversation Exist
					//remove it from convArray and update messages.
					convArray.splice(convArray.indexOf($scope.conversations[i].number),1);
					$scope.conversations[i].updateMessages();
				}
			}
			//loop through all convs that were not removed and create new conversations for them.
			for(var i = 0; convArray.length > i; i++){
				$scope.conversations.push(new Conversation(convArray[i]));
			}
			
		}, function(result){
			console.log("ERROR");
		});

		}, 15000)
	$scope.messageTextBox;
	$scope.sendMessage = function(conversation){
		
		var data = {"CONVERSATIONNUMBER":conversation.number,
					"FROM":"18307652286",
					"TO":conversation.number,
					"MESSAGE":$scope.messageTextBox,
					"CLIENT":"WEB"
					}
		$scope.messageTextBox = "";
		$http.post("http://localhost/message/by/PhoneNumber/",data,{"headers":Auth}).then(function(result){
			console.log(result);
		}, function(result){
			console.log(result);
		});	
	}
	
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
	
	class Conversation{
		constructor(number){
			var c = this;
			this.unreadCount = 0;
			this.number = number;
			this.name = number;
			this.lastMessageTime = "3:00PM";
			this.messages = [];
			this.lastMesssage = null;
			this.updateMessages = function() {
				$http.get("http://localhost/message/by/ID/"+c.number+"/"+(Number(c.lastMesssage.id)+1)+"/",{"headers":Auth}).then(function(result){
					for(var j = 0; result.data.length > j; j++){
						var tempMsg = new Message(result.data[j].ID,result.data[j].MESSAGE,result.data[j].TO,result.data[j].FROM,result.data[j].TIME);
						c.AddMessage(tempMsg);

						
					}
				}, function(result){
					console.log("ERROR");
				});	
			}
			this.AddMessage = function(message) {
				if(this != $scope.activeConversation){
					this.unreadCount+=1;
				}
				this.messages.push(message);
				this.lastMesssage = message;
				this.lastMessageTime = message.time;
			}
			$http.get("http://localhost/message/by/ID/"+number+"/0/",{"headers":Auth}).then(function(result){
				for(var j = 0; result.data.length > j; j++){
					c.AddMessage(new Message(result.data[j].ID,result.data[j].MESSAGE,result.data[j].TO,result.data[j].FROM,result.data[j].TIME))
				}
				c.unreadCount = 0;
			}, function(result){
				console.log("ERROR");
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
});


